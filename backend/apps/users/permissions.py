from rest_framework.permissions import BasePermission


class IsAdministratorRole(BasePermission):
    """
    Permite el acceso únicamente a usuarios activos
    con el rol institucional ADMINISTRADOR.
    """

    message = (
        "No tiene permisos para realizar esta operación. "
        "Se requiere el rol ADMINISTRADOR."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        return user.groups.filter(
            name="ADMINISTRADOR",
        ).exists()