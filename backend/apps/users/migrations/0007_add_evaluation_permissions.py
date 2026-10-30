from django.db import migrations


EVALUATION_PERMISSIONS = (
    (
        "view_evaluations",
        "Puede consultar evaluaciones",
    ),
    (
        "manage_evaluations",
        "Puede administrar evaluaciones",
    ),
)

EVALUATION_ROLES = (
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
)


def add_evaluation_permissions(
    apps,
    schema_editor,
):
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
    )
    Group = apps.get_model(
        "auth",
        "Group",
    )
    Permission = apps.get_model(
        "auth",
        "Permission",
    )

    user_content_type = ContentType.objects.get(
        app_label="users",
        model="user",
    )

    permissions = []

    for codename, name in EVALUATION_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            content_type=user_content_type,
            codename=codename,
            defaults={
                "name": name,
            },
        )
        permissions.append(permission)

    for role_name in EVALUATION_ROLES:
        group = Group.objects.get(
            name=role_name,
        )
        group.permissions.add(
            *permissions,
        )


def remove_evaluation_permissions(
    apps,
    schema_editor,
):
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
    )
    Group = apps.get_model(
        "auth",
        "Group",
    )
    Permission = apps.get_model(
        "auth",
        "Permission",
    )

    try:
        user_content_type = ContentType.objects.get(
            app_label="users",
            model="user",
        )
    except ContentType.DoesNotExist:
        return

    permissions = Permission.objects.filter(
        content_type=user_content_type,
        codename__in=[
            codename
            for codename, _ in EVALUATION_PERMISSIONS
        ],
    )

    for role_name in EVALUATION_ROLES:
        group = Group.objects.filter(
            name=role_name,
        ).first()

        if group is not None:
            group.permissions.remove(
                *permissions,
            )

    permissions.delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0006_add_therapy_followup_permissions",
        ),
    ]

    operations = [
        migrations.RunPython(
            add_evaluation_permissions,
            reverse_code=remove_evaluation_permissions,
        ),
    ]
