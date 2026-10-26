from django.db import migrations


THERAPY_PERMISSIONS = (
    (
        "view_therapy_followups",
        "Puede consultar seguimientos terapéuticos",
    ),
    (
        "manage_therapy_followups",
        "Puede administrar seguimientos terapéuticos",
    ),
)

THERAPIST_ROLE = "TERAPEUTA"


def add_therapy_followup_permissions(
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

    therapist_group = Group.objects.get(
        name=THERAPIST_ROLE,
    )

    for codename, name in THERAPY_PERMISSIONS:
        permission, _ = Permission.objects.update_or_create(
            content_type=user_content_type,
            codename=codename,
            defaults={
                "name": name,
            },
        )

        therapist_group.permissions.add(
            permission,
        )


def remove_therapy_followup_permissions(
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
            for codename, _ in THERAPY_PERMISSIONS
        ],
    )

    therapist_group = Group.objects.filter(
        name=THERAPIST_ROLE,
    ).first()

    if therapist_group is not None:
        therapist_group.permissions.remove(
            *permissions,
        )

    permissions.delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0005_add_student_assignment_permission",
        ),
    ]

    operations = [
        migrations.RunPython(
            add_therapy_followup_permissions,
            reverse_code=remove_therapy_followup_permissions,
        ),
    ]
