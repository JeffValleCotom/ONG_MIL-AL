RESPONSIBLE_CONTEXT = "RESPONSABLE_INSTITUCIONAL"


def has_responsible_permission(user, codename):
    return user.groups.filter(
        name=RESPONSIBLE_CONTEXT,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename=codename,
    ).exists()
