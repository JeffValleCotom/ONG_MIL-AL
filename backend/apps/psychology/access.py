from rest_framework import exceptions, serializers


PSYCHOLOGY_CONTEXT = "PSICOLOGO"

KNOWN_STUDENT_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
}


def require_psychology_context(request):
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
                    "Debe indicar el contexto PSICOLOGO "
                    "para acceder a información psicológica."
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

    if context != PSYCHOLOGY_CONTEXT:
        raise exceptions.PermissionDenied(
            "La información psicológica solo está "
            "disponible en el contexto PSICOLOGO."
        )

    if not request.user.groups.filter(
        name=PSYCHOLOGY_CONTEXT,
    ).exists():
        raise exceptions.PermissionDenied(
            "No tiene acceso al contexto PSICOLOGO."
        )

    return context


def has_psychologist_permission(
    user,
    codename,
):
    return user.groups.filter(
        name=PSYCHOLOGY_CONTEXT,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename=codename,
    ).exists()


def require_psychology_access(
    request,
    permission_codename,
):
    context = require_psychology_context(request)

    if not has_psychologist_permission(
        request.user,
        permission_codename,
    ):
        raise exceptions.PermissionDenied(
            "No tiene el permiso psicológico requerido "
            "dentro del contexto PSICOLOGO."
        )

    return context
