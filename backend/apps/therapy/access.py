from rest_framework import exceptions, serializers


THERAPY_CONTEXT = "TERAPEUTA"

KNOWN_STUDENT_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
}


def require_therapy_context(request):
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
                    "Debe indicar el contexto TERAPEUTA "
                    "para acceder a información terapéutica."
                )
            }
        )

    if context not in KNOWN_STUDENT_CONTEXTS:
        raise serializers.ValidationError(
            {
                "context": (
                    "El contexto de acceso no es válido."
                )
            }
        )

    if context != THERAPY_CONTEXT:
        raise exceptions.PermissionDenied(
            "La información terapéutica solo está "
            "disponible en el contexto TERAPEUTA."
        )

    if not request.user.groups.filter(
        name=THERAPY_CONTEXT,
    ).exists():
        raise exceptions.PermissionDenied(
            "No tiene acceso al contexto TERAPEUTA."
        )

    return context


def has_therapist_permission(
    user,
    codename,
):
    return user.groups.filter(
        name=THERAPY_CONTEXT,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename=codename,
    ).exists()


def require_therapy_access(
    request,
    permission_codename,
):
    context = require_therapy_context(request)

    if not has_therapist_permission(
        request.user,
        permission_codename,
    ):
        raise exceptions.PermissionDenied(
            "No tiene el permiso terapéutico requerido "
            "dentro del contexto TERAPEUTA."
        )

    return context
