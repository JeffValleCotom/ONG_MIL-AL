from rest_framework import (
    exceptions,
    mixins,
    permissions,
    serializers,
    viewsets,
)

from apps.students.models import StudentProfessionalAssignment
from apps.users.permissions import HasPlatformPermission

from .access import require_academic_access
from .models import AcademicFollowUp
from .serializers import AcademicFollowUpSerializer


class AcademicFollowUpViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AcademicFollowUpSerializer

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
        "list": "view_academic_followups",
        "retrieve": "view_academic_followups",
        "create": "manage_academic_followups",
        "update": "manage_academic_followups",
        "partial_update": "manage_academic_followups",
    }

    def get_required_permission(self):
        return self.required_permission_map.get(
            self.action
        )

    def enforce_academic_access(self):
        required_permission = self.get_required_permission()

        if not required_permission:
            raise exceptions.PermissionDenied(
                "No tiene permisos para realizar "
                "esta operación académica."
            )

        return require_academic_access(
            self.request,
            required_permission,
        )

    def create(self, request, *args, **kwargs):
        self.enforce_academic_access()

        student_id = request.data.get("student_id")

        if student_id not in (None, ""):
            try:
                student_id = int(student_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {
                        "student_id": (
                            "El identificador del estudiante "
                            "debe ser un número entero."
                        )
                    }
                )

            if student_id < 1:
                raise serializers.ValidationError(
                    {
                        "student_id": (
                            "El identificador del estudiante "
                            "debe ser mayor que cero."
                        )
                    }
                )

            has_assignment = (
                StudentProfessionalAssignment.objects
                .filter(
                    student_id=student_id,
                    professional=request.user,
                    professional_role="DOCENTE",
                    is_active=True,
                )
                .exists()
            )

            if not has_assignment:
                raise exceptions.NotFound(
                    "No Student matches the given query."
                )

        return super().create(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        self.enforce_academic_access()

        queryset = (
            AcademicFollowUp.objects
            .select_related(
                "student",
                "created_by",
                "updated_by",
            )
            .filter(
                student__professional_assignments__professional=(
                    self.request.user
                ),
                student__professional_assignments__professional_role=(
                    "DOCENTE"
                ),
                student__professional_assignments__is_active=True,
            )
            .distinct()
        )

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

        return queryset

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        self.enforce_academic_access()

        if "student_id" in request.data:
            raise serializers.ValidationError(
                {
                    "student_id": (
                        "No se puede cambiar el estudiante "
                        "de un seguimiento académico."
                    )
                }
            )

        return super().partial_update(
            request,
            *args,
            **kwargs,
        )

    def perform_create(self, serializer):
        self.enforce_academic_access()

        student = serializer.validated_data["student"]

        if not student.is_active:
            raise serializers.ValidationError(
                {
                    "student_id": (
                        "No se puede registrar un seguimiento "
                        "académico para un estudiante inactivo."
                    )
                }
            )

        has_assignment = (
            StudentProfessionalAssignment.objects
            .filter(
                student=student,
                professional=self.request.user,
                professional_role="DOCENTE",
                is_active=True,
            )
            .exists()
        )

        if not has_assignment:
            raise exceptions.NotFound(
                "No Student matches the given query."
            )

        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        self.enforce_academic_access()

        serializer.save(
            updated_by=self.request.user,
        )
