from django.db.models import Q
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

from .models import Student, StudentProfessionalAssignment
from .serializers import (
    AssignmentUserSummarySerializer,
    StudentProfessionalAssignmentSerializer,
    StudentRecordSerializer,
    StudentSerializer,
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.academic.access import has_docente_permission
from apps.psychology.access import (
    has_psychologist_permission,
)
from apps.therapy.access import (
    has_therapist_permission,
)
from .access import has_responsible_permission

User = get_user_model()

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
    }

    def get_required_permission(self):
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

        if (
            self.action
            in {
                "create",
                "update",
                "partial_update",
                "activate",
                "deactivate",
            }
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
        methods=["get"],
        url_path="record",
    )
    def record(self, request, pk=None):
        student = self.get_object()

        context = self.get_student_access_context()

        sections = {
            "general": student,
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
