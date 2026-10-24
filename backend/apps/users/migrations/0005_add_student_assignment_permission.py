from django.db import migrations


PERMISSION_CODENAME = "manage_student_assignments"
PERMISSION_NAME = (
    "Puede administrar asignaciones de profesionales a estudiantes"
)
RESPONSIBLE_ROLE = "RESPONSABLE_INSTITUCIONAL"


def add_student_assignment_permission(apps, schema_editor):
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

    permission, _ = Permission.objects.update_or_create(
        content_type=user_content_type,
        codename=PERMISSION_CODENAME,
        defaults={
            "name": PERMISSION_NAME,
        },
    )

    responsible_group = Group.objects.get(
        name=RESPONSIBLE_ROLE,
    )

    responsible_group.permissions.add(
        permission,
    )


def remove_student_assignment_permission(
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

    permission = Permission.objects.filter(
        content_type=user_content_type,
        codename=PERMISSION_CODENAME,
    ).first()

    if permission is None:
        return

    responsible_group = Group.objects.filter(
        name=RESPONSIBLE_ROLE,
    ).first()

    if responsible_group is not None:
        responsible_group.permissions.remove(
            permission,
        )

    permission.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_assign_role_permissions"),
    ]

    operations = [
        migrations.RunPython(
            add_student_assignment_permission,
            reverse_code=remove_student_assignment_permission,
        ),
    ]