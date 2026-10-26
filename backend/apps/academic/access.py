from rest_framework import exceptions, serializers


ACADEMIC_CONTEXT = "DOCENTE"

KNOWN_STUDENT_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
}


def require_academic_context(request):
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
                    "Debe indicar el contexto DOCENTE "
                    "para acceder a información académica."
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

    if context != ACADEMIC_CONTEXT:
        raise exceptions.PermissionDenied(
            "La información académica solo está "
            "disponible en el contexto DOCENTE."
        )

    if not request.user.groups.filter(
        name=ACADEMIC_CONTEXT,
    ).exists():
        raise exceptions.PermissionDenied(
            "No tiene acceso al contexto DOCENTE."
        )

    return context


def has_docente_permission(user, codename):
    return user.groups.filter(
        name=ACADEMIC_CONTEXT,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename=codename,
    ).exists()


def require_academic_access(
    request,
    permission_codename,
):
    context = require_academic_context(request)

    if not has_docente_permission(
        request.user,
        permission_codename,
    ):
        raise exceptions.PermissionDenied(
            "No tiene el permiso académico requerido "
            "dentro del contexto DOCENTE."
        )

    return context
