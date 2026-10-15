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


class HasPlatformPermission(BasePermission):
    """
    Autoriza una funcionalidad cuando alguno de los roles
    institucionales del usuario posee el permiso requerido.
    """

    message = (
        "No tiene permisos para realizar esta operación."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        if request.method.lower() not in view.http_method_names:
            return True

        get_required_permission = getattr(
            view,
            "get_required_permission",
            None,
        )

        if not callable(get_required_permission):
            return False

        required_permission = get_required_permission()

        if not required_permission:
            return False

        return user.groups.filter(
            permissions__content_type__app_label="users",
            permissions__content_type__model="user",
            permissions__codename=required_permission,
        ).exists()
    