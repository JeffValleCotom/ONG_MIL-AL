import hashlib
import logging
from django.db.models import Q
from django.http import FileResponse
from rest_framework import (
    exceptions,
    mixins,
    permissions,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.permissions import HasPlatformPermission
from .models import (
    Student,
    StudentDocument,
    StudentProfessionalAssignment,
)
from .serializers import (
    AssignmentUserSummarySerializer,
    StudentProfessionalAssignmentSerializer,
    StudentRecordSerializer,
    StudentSerializer,
    StudentFamilyMemberSerializer,
    StudentDocumentSerializer,
    StudentDocumentUploadSerializer,
)
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.academic.access import has_docente_permission
from apps.psychology.access import (
    has_psychologist_permission,
)
from apps.therapy.access import (
    has_therapist_permission,
)
from .access import has_responsible_permission
from .document_validation import (
    DocumentValidationError,
    validate_uploaded_document,
)
from rest_framework.parsers import FormParser, MultiPartParser

User = get_user_model()

logger = logging.getLogger(__name__)

STUDENT_ACCESS_CONTEXTS = (
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
)

PROFESSIONAL_STUDENT_CONTEXTS = (
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
)


class StudentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    required_permission_map = {
        "list": "view_students",
        "retrieve": "view_students",
        "record": "view_students",
        "create": "manage_students",
        "update": "manage_students",
        "partial_update": "manage_students",
        "activate": "manage_students",
        "deactivate": "manage_students",
        "family_members": "manage_students",
        "family_member_detail": "manage_students",
        "deactivate_family_member": "manage_students",
        "documents": "view_students",
        "document_download": "view_students",
    }

    def get_required_permission(self):
        if self.action == "family_members":
            if self.request.method == "GET":
                return "view_students"

            return "manage_students"

        return self.required_permission_map.get(
            self.action
        )

    def get_student_access_context(self):
        user_roles = set(
            self.request.user.groups.filter(
                name__in=STUDENT_ACCESS_CONTEXTS,
            ).values_list(
                "name",
                flat=True,
            )
        )

        requested_context = (
            self.request.query_params
            .get("context", "")
            .strip()
            .upper()
        )

        if requested_context:
            if requested_context not in STUDENT_ACCESS_CONTEXTS:
                raise serializers.ValidationError(
                    {
                        "context": (
                            "El contexto de acceso no es válido."
                        )
                    }
                )

            if requested_context not in user_roles:
                raise exceptions.PermissionDenied(
                    "No tiene acceso al contexto solicitado."
                )

            return requested_context

        is_family_write = (
            self.action == "family_members"
            and self.request.method == "POST"
        )

        if (
            (
                self.action
                in {
                    "create",
                    "update",
                    "partial_update",
                    "activate",
                    "deactivate",
                    "family_member_detail",
                    "deactivate_family_member",
                }
                or is_family_write
            )
            and "RESPONSABLE_INSTITUCIONAL" in user_roles
        ):
            return "RESPONSABLE_INSTITUCIONAL"

        if len(user_roles) == 1:
            return next(iter(user_roles))

        if len(user_roles) > 1:
            raise serializers.ValidationError(
                {
                    "context": (
                        "Debe indicar el contexto de acceso "
                        "cuando el usuario posee varios roles."
                    )
                }
            )

        return None

    def require_document_upload_permission(
        self,
        context,
        document_type,
    ):
        if (
            document_type
            == StudentDocument.DocumentType.ACADEMICO
        ):
            allowed = (
                context == "DOCENTE"
                and has_docente_permission(
                    self.request.user,
                    "manage_academic_followups",
                )
            )
        elif (
            document_type
            == StudentDocument.DocumentType.PSICOLOGICO
        ):
            allowed = (
                context == "PSICOLOGO"
                and has_psychologist_permission(
                    self.request.user,
                    "manage_psychological_followups",
                )
            )
        elif (
            document_type
            == StudentDocument.DocumentType.TERAPEUTICO
        ):
            allowed = (
                context == "TERAPEUTA"
                and has_therapist_permission(
                    self.request.user,
                    "manage_interventions",
                )
            )
        else:
            allowed = (
                context == "RESPONSABLE_INSTITUCIONAL"
                and has_responsible_permission(
                    self.request.user,
                    "manage_students",
                )
            )

        if not allowed:
            raise exceptions.PermissionDenied(
                "No tiene permiso para cargar documentos "
                "de este tipo en el contexto seleccionado."
            )

    def get_visible_document_types(self, context):
        user = self.request.user

        if (
            context == "DOCENTE"
            and has_docente_permission(
                user,
                "view_academic_followups",
            )
        ):
            return (
                StudentDocument.DocumentType.ACADEMICO,
            )

        if (
            context == "PSICOLOGO"
            and has_psychologist_permission(
                user,
                "view_psychological_followups",
            )
        ):
            return (
                StudentDocument.DocumentType.PSICOLOGICO,
            )

        if (
            context == "TERAPEUTA"
            and has_therapist_permission(
                user,
                "view_interventions",
            )
        ):
            return (
                StudentDocument.DocumentType.TERAPEUTICO,
            )

        if (
            context == "RESPONSABLE_INSTITUCIONAL"
            and has_responsible_permission(
                user,
                "view_students",
            )
        ):
            return (
                StudentDocument.DocumentType.IDENTIFICACION,
                StudentDocument.DocumentType.CONSENTIMIENTO_AUTORIZACION,
                StudentDocument.DocumentType.MEDICO,
                StudentDocument.DocumentType.INSTITUCIONAL,
                StudentDocument.DocumentType.OTRO,
            )

        raise exceptions.PermissionDenied(
            "No tiene permiso para consultar documentos "
            "en el contexto seleccionado."
        )

    def apply_student_scope(
        self,
        queryset,
    ):
        context = self.get_student_access_context()

        if context == "RESPONSABLE_INSTITUCIONAL":
            return queryset

        if context in PROFESSIONAL_STUDENT_CONTEXTS:
            return queryset.filter(
                professional_assignments__professional=(
                    self.request.user
                ),
                professional_assignments__professional_role=(
                    context
                ),
                professional_assignments__is_active=True,
            ).distinct()

    def get_queryset(self):
        queryset = Student.objects.all().order_by(
            "last_name",
            "first_name",
            "institutional_code",
        )

        queryset = self.apply_student_scope(
            queryset
        )

        if self.action != "list":
            return queryset

        search = (
            self.request.query_params
            .get("search", "")
            .strip()
        )

        if search:
            queryset = queryset.filter(
                Q(institutional_code__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        status_filter = (
            self.request.query_params
            .get("status", "")
            .strip()
            .lower()
        )

        if status_filter:
            status_values = {
                "active": True,
                "inactive": False,
            }

            if status_filter not in status_values:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "El estado debe ser "
                            "'active' o 'inactive'."
                        )
                    }
                )

            queryset = queryset.filter(
                is_active=status_values[
                    status_filter
                ]
            )

        return queryset

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="family-members",
    )
    def family_members(self, request, pk=None):
        student = self.get_object()

        context = self.get_student_access_context()

        if request.method == "GET":
            if (
                context != "RESPONSABLE_INSTITUCIONAL"
                or not has_responsible_permission(
                    request.user,
                    "view_students",
                )
            ):
                raise exceptions.PermissionDenied(
                    "No tiene permiso para consultar "
                    "la información familiar."
                )

            family_members = student.family_members.all()

            serializer = StudentFamilyMemberSerializer(
                family_members,
                many=True,
            )

            return Response(
                {
                    "items": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        if (
            context != "RESPONSABLE_INSTITUCIONAL"
            or not has_responsible_permission(
                request.user,
                "manage_students",
            )
        ):
            raise exceptions.PermissionDenied(
                "No tiene permiso para gestionar "
                "la información familiar."
            )

        serializer = StudentFamilyMemberSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                "student": student,
            },
        )
        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                serializer.save(
                    student=student,
                    created_by=request.user,
                    updated_by=request.user,
                )
        except IntegrityError as exc:
            if serializer.validated_data.get(
                "is_primary_contact",
                False,
            ):
                raise serializers.ValidationError(
                    {
                        "is_primary_contact": (
                            "El estudiante ya posee un "
                            "contacto principal activo."
                        )
                    }
                ) from exc

            raise

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path=(
            r"family-members/"
            r"(?P<family_member_id>\d+)"
        ),
    )
    def family_member_detail(
        self,
        request,
        pk=None,
        family_member_id=None,
    ):
        student = self.get_object()
        context = self.get_student_access_context()

        if (
            context != "RESPONSABLE_INSTITUCIONAL"
            or not has_responsible_permission(
                request.user,
                "manage_students",
            )
        ):
            raise exceptions.PermissionDenied(
                "No tiene permiso para gestionar "
                "la información familiar."
            )

        family_member = get_object_or_404(
            student.family_members.all(),
            pk=family_member_id,
        )

        serializer = StudentFamilyMemberSerializer(
            family_member,
            data=request.data,
            partial=True,
            context={
                **self.get_serializer_context(),
                "student": student,
            },
        )
        serializer.is_valid(
            raise_exception=True
        )

        try:
            with transaction.atomic():
                serializer.save(
                    updated_by=request.user,
                )
        except IntegrityError as exc:
            if serializer.validated_data.get(
                "is_primary_contact",
                family_member.is_primary_contact,
            ):
                raise serializers.ValidationError(
                    {
                        "is_primary_contact": (
                            "El estudiante ya posee un "
                            "contacto principal activo."
                        )
                    }
                ) from exc

            raise

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path=(
            r"family-members/"
            r"(?P<family_member_id>\d+)/deactivate"
        ),
    )
    def deactivate_family_member(
        self,
        request,
        pk=None,
        family_member_id=None,
    ):
        student = self.get_object()
        context = self.get_student_access_context()

        if (
            context != "RESPONSABLE_INSTITUCIONAL"
            or not has_responsible_permission(
                request.user,
                "manage_students",
            )
        ):
            raise exceptions.PermissionDenied(
                "No tiene permiso para gestionar "
                "la información familiar."
            )

        family_member = get_object_or_404(
            student.family_members.all(),
            pk=family_member_id,
        )

        if family_member.is_active:
            family_member.is_active = False
            family_member.is_primary_contact = False
            family_member.deactivated_at = timezone.now()
            family_member.updated_by = request.user

            family_member.save(
                update_fields=[
                    "is_active",
                    "is_primary_contact",
                    "deactivated_at",
                    "updated_by",
                    "updated_at",
                ]
            )

        serializer = StudentFamilyMemberSerializer(
            family_member,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="documents",
        parser_classes=[
            MultiPartParser,
            FormParser,
        ],
    )
    def documents(self, request, pk=None):
        student = self.get_object()
        context = self.get_student_access_context()

        if request.method == "GET":
            visible_types = (
                self.get_visible_document_types(
                    context
                )
            )

            documents = student.documents.filter(
                document_type__in=visible_types,
            )

            serializer = StudentDocumentSerializer(
                documents,
                many=True,
            )

            return Response(
                {
                    "items": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        serializer = StudentDocumentUploadSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(
            raise_exception=True,
        )

        document_type = serializer.validated_data[
            "document_type"
        ]

        self.require_document_upload_permission(
            context,
            document_type,
        )

        uploaded_file = serializer.validated_data[
            "file"
        ]

        try:
            validation_result = (
                validate_uploaded_document(
                    uploaded_file
                )
            )
        except DocumentValidationError as exc:
            raise serializers.ValidationError(
                {
                    "file": str(exc),
                }
            ) from exc

        sha256 = hashlib.sha256()

        for chunk in uploaded_file.chunks():
            sha256.update(chunk)

        uploaded_file.seek(0)

        uploaded_file.name = (
            f"document{validation_result.extension}"
        )

        document_data = dict(
            serializer.validated_data
        )
        document_data.pop("file")

        document = StudentDocument(
            student=student,
            file=uploaded_file,
            original_filename=(
                validation_result.original_filename
            ),
            mime_type=validation_result.mime_type,
            size_bytes=validation_result.size_bytes,
            sha256=sha256.hexdigest(),
            created_by=request.user,
            updated_by=request.user,
            **document_data,
        )

        try:
            with transaction.atomic():
                document.save()
        except Exception:
            stored_name = (
                document.file.name
                if document.file
                else ""
            )

            normalized_name = stored_name.replace(
                "\\",
                "/",
            )

            expected_prefix = (
                f"students/{student.pk}/documents/"
            )

            if normalized_name.startswith(
                expected_prefix
            ):
                try:
                    document.file.storage.delete(
                        stored_name
                    )
                except Exception:
                    logger.exception(
                        "No fue posible eliminar un "
                        "archivo documental huérfano."
                    )

            raise

        response_serializer = (
            StudentDocumentUploadSerializer(
                document
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path=(
            r"documents/"
            r"(?P<document_id>\d+)/download"
        ),
    )
    def document_download(
        self,
        request,
        pk=None,
        document_id=None,
    ):
        student = self.get_object()
        context = self.get_student_access_context()

        visible_types = (
            self.get_visible_document_types(
                context
            )
        )

        document = get_object_or_404(
            StudentDocument.objects.filter(
                student=student,
                document_type__in=visible_types,
            ),
            pk=document_id,
        )

        if (
            not document.file
            or not document.file.storage.exists(
                document.file.name
            )
        ):
            raise exceptions.NotFound(
                "El archivo del documento "
                "no está disponible."
            )

        file_handle = document.file.open("rb")

        response = FileResponse(
            file_handle,
            as_attachment=True,
            filename=document.original_filename,
            content_type=(
                document.mime_type
                or "application/octet-stream"
            ),
        )

        response["Cache-Control"] = (
            "private, no-store"
        )
        response["X-Content-Type-Options"] = (
            "nosniff"
        )

        return response

    @action(
        detail=True,
        methods=["get"],
        url_path="record",
    )
    def record(self, request, pk=None):
        student = self.get_object()

        context = self.get_student_access_context()

        can_manage_students = (
            context == "RESPONSABLE_INSTITUCIONAL"
            and has_responsible_permission(
                request.user,
                "manage_students",
            )
        )

        can_manage_academic = (
            context == "DOCENTE"
            and has_docente_permission(
                request.user,
                "manage_academic_followups",
            )
        )

        capabilities = {
            "update_general": can_manage_students,
            "manage_family": can_manage_students,
            "manage_academic": can_manage_academic,
        }

        sections = {
            "general": student,
        }

        if (
            context == "RESPONSABLE_INSTITUCIONAL"
            and has_responsible_permission(
                request.user,
                "view_students",
            )
        ):
            sections["family"] = {
                "items": student.family_members.all(),
            }

        if (
            context == "RESPONSABLE_INSTITUCIONAL"
            and has_responsible_permission(
                request.user,
                "manage_student_assignments",
            )
        ):
            sections["assignments"] = {
                "items": (
                    student.professional_assignments
                    .select_related(
                        "professional",
                        "assigned_by",
                    )
                    .all()
                ),
            }

        if (
            context == "DOCENTE"
            and has_docente_permission(
                request.user,
                "view_academic_followups",
            )
        ):
            sections["academic"] = {
                "followups": (
                    student.academic_followups
                    .filter(
                        created_by=request.user,
                    )
                    .select_related(
                        "created_by",
                        "updated_by",
                    )
                    .all()
                ),
            }
        if (
            context == "PSICOLOGO"
            and has_psychologist_permission(
                request.user,
                "view_psychological_followups",
            )
        ):
            sections["psychological"] = {
                "followups": (
                    student.psychological_followups
                    .filter(
                        created_by=request.user,
                    )
                    .select_related(
                        "created_by",
                        "updated_by",
                    )
                    .all()
                ),
            }

        if (
            context == "TERAPEUTA"
            and has_therapist_permission(
                request.user,
                "view_therapy_followups",
            )
        ):
            sections["therapy"] = {
                "followups": (
                    student.therapy_followups
                    .filter(
                        created_by=request.user,
                    )
                    .select_related(
                        "created_by",
                        "updated_by",
                    )
                    .all()
                ),
            }

        serializer = StudentRecordSerializer(
            {
                "student_id": student.id,
                "context": context,
                "capabilities": capabilities,
                "sections": sections,
            }
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="activate",
    )
    def activate(self, request, pk=None):
        student = self.get_object()

        if student.is_active:
            return Response(
                {
                    "detail": (
                        "El estudiante ya se encuentra activo."
                    ),
                    "student": self.get_serializer(
                        student
                    ).data,
                },
                status=status.HTTP_200_OK,
            )

        student.is_active = True
        student.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Estudiante activado correctamente."
                ),
                "student": self.get_serializer(
                    student
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="deactivate",
    )
    def deactivate(self, request, pk=None):
        student = self.get_object()

        if not student.is_active:
            return Response(
                {
                    "detail": (
                        "El estudiante ya se encuentra inactivo."
                    ),
                    "student": self.get_serializer(
                        student
                    ).data,
                },
                status=status.HTTP_200_OK,
            )

        student.is_active = False
        student.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Estudiante desactivado correctamente."
                ),
                "student": self.get_serializer(
                    student
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class StudentProfessionalAssignmentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StudentProfessionalAssignmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasPlatformPermission,
    ]

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]

    required_permission_map = {
        "list": "manage_student_assignments",
        "retrieve": "manage_student_assignments",
        "create": "manage_student_assignments",
        "finish": "manage_student_assignments",
        "eligible_professionals": (
            "manage_student_assignments"
        ),
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def get_queryset(self):
        queryset = (
            StudentProfessionalAssignment.objects
            .select_related(
                "student",
                "professional",
                "assigned_by",
            )
            .order_by(
                "-assigned_at",
                "-id",
            )
        )

        if self.action != "list":
            return queryset

        student_id = (
            self.request.query_params
            .get("student", "")
            .strip()
        )

        if student_id:
            try:
                student_id = int(student_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {
                        "student": (
                            "El identificador del estudiante "
                            "debe ser un número entero."
                        )
                    }
                )

            if student_id < 1:
                raise serializers.ValidationError(
                    {
                        "student": (
                            "El identificador del estudiante "
                            "debe ser mayor que cero."
                        )
                    }
                )

            queryset = queryset.filter(
                student_id=student_id,
            )

        status_filter = (
            self.request.query_params
            .get("status", "")
            .strip()
            .lower()
        )

        if status_filter:
            status_values = {
                "active": True,
                "inactive": False,
            }

            if status_filter not in status_values:
                raise serializers.ValidationError(
                    {
                        "status": (
                            "El estado debe ser "
                            "'active' o 'inactive'."
                        )
                    }
                )

            queryset = queryset.filter(
                is_active=status_values[
                    status_filter
                ]
            )

        professional_role = (
            self.request.query_params
            .get("professional_role", "")
            .strip()
            .upper()
        )

        if professional_role:
            if (
                professional_role
                not in StudentProfessionalAssignment
                .ProfessionalRole.values
            ):
                raise serializers.ValidationError(
                    {
                        "professional_role": (
                            "El rol profesional no es válido."
                        )
                    }
                )

            queryset = queryset.filter(
                professional_role=professional_role,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            assigned_by=self.request.user,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="eligible-professionals",
    )
    def eligible_professionals(self, request):
        professional_role = (
            request.query_params
            .get("role", "")
            .strip()
            .upper()
        )

        if not professional_role:
            raise serializers.ValidationError(
                {
                    "role": (
                        "Debe indicar el rol profesional."
                    )
                }
            )

        if (
            professional_role
            not in StudentProfessionalAssignment
            .ProfessionalRole.values
        ):
            raise serializers.ValidationError(
                {
                    "role": (
                        "El rol profesional no es válido."
                    )
                }
            )

        professionals = (
            User.objects.filter(
                is_active=True,
                groups__name=professional_role,
            )
            .distinct()
            .order_by(
                "last_name",
                "first_name",
                "username",
                "id",
            )
        )

        serializer = AssignmentUserSummarySerializer(
            professionals,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="finish",
    )
    def finish(self, request, pk=None):
        assignment = self.get_object()

        if not assignment.is_active:
            return Response(
                {
                    "detail": (
                        "La asignación ya se encuentra "
                        "finalizada."
                    ),
                    "assignment": self.get_serializer(
                        assignment
                    ).data,
                },
                status=status.HTTP_200_OK,
            )

        assignment.is_active = False
        assignment.unassigned_at = timezone.now()
        assignment.save(
            update_fields=[
                "is_active",
                "unassigned_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Asignación finalizada correctamente."
                ),
                "assignment": self.get_serializer(
                    assignment
                ).data,
            },
            status=status.HTTP_200_OK,
        )
