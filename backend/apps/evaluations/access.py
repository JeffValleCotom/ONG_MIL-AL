from rest_framework import exceptions, serializers

from apps.students.models import (
    StudentProfessionalAssignment,
)


EVALUATION_CONTEXTS = {
    role.value
    for role in (
        StudentProfessionalAssignment
        .ProfessionalRole
    )
}


def require_evaluation_context(request):
    context = (
        request.query_params
        .get("context", "")
        .strip()
        .upper()
    )

    if not context:
        raise serializers.ValidationError(
            {
                "context": (
                    "Debe indicar un contexto profesional "
                    "para acceder a evaluaciones."
                )
            }
        )

    if context not in EVALUATION_CONTEXTS:
        raise serializers.ValidationError(
            {
                "context": (
                    "El contexto de evaluación no es válido."
                )
            }
        )

    if not request.user.groups.filter(
        name=context,
    ).exists():
        raise exceptions.PermissionDenied(
            "No tiene acceso al contexto profesional "
            "indicado."
        )

    return context


def has_evaluation_permission(
    user,
    context,
    codename,
):
    if context not in EVALUATION_CONTEXTS:
        return False

    return user.groups.filter(
        name=context,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename=codename,
    ).exists()


def require_evaluation_access(
    request,
    permission_codename,
):
    context = require_evaluation_context(request)

    if not has_evaluation_permission(
        request.user,
        context,
        permission_codename,
    ):
        raise exceptions.PermissionDenied(
            "No tiene el permiso de evaluaciones "
            "requerido dentro del contexto profesional."
        )

    return context
