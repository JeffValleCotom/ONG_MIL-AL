from django.db import migrations


ROLE_PERMISSIONS = {
    "ADMINISTRADOR": (
        "manage_users",
        "manage_roles",
        "manage_permissions",
        "view_audit",
    ),
    "DOCENTE": (
        "view_students",
        "view_academic_followups",
        "manage_academic_followups",
        "view_reports",
        "view_dashboard",
        "view_alerts",
        "use_ai_assistant",
    ),
    "PSICOLOGO": (
        "view_students",
        "view_psychological_followups",
        "manage_psychological_followups",
        "view_interventions",
        "manage_interventions",
        "view_reports",
        "view_dashboard",
        "view_alerts",
        "use_ai_assistant",
    ),
    "TERAPEUTA": (
        "view_students",
        "view_interventions",
        "manage_interventions",
        "view_reports",
        "view_dashboard",
        "view_alerts",
        "use_ai_assistant",
    ),
    "RESPONSABLE_INSTITUCIONAL": (
        "view_students",
        "manage_students",
        "view_reports",
        "view_dashboard",
        "view_alerts",
    ),
}


def assign_role_permissions(apps, schema_editor):
    Group = apps.get_model(
        "auth",
        "Group",
    )
    Permission = apps.get_model(
        "auth",
        "Permission",
    )
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
    )

    user_content_type = ContentType.objects.get(
        app_label="users",
        model="user",
    )

    platform_codenames = {
        codename
        for permission_codenames in ROLE_PERMISSIONS.values()
        for codename in permission_codenames
    }

    platform_permissions = Permission.objects.filter(
        content_type=user_content_type,
        codename__in=platform_codenames,
    )

    for role_name, permission_codenames in ROLE_PERMISSIONS.items():
        group = Group.objects.get(
            name=role_name,
        )

        # Sustituye únicamente los permisos de plataforma MIL-AL.
        # Otros permisos de Django permanecen intactos.
        group.permissions.remove(
            *platform_permissions
        )

        role_permissions = Permission.objects.filter(
            content_type=user_content_type,
            codename__in=permission_codenames,
        )

        group.permissions.add(
            *role_permissions
        )


def remove_role_permissions(apps, schema_editor):
    Group = apps.get_model(
        "auth",
        "Group",
    )
    Permission = apps.get_model(
        "auth",
        "Permission",
    )
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
    )

    user_content_type = ContentType.objects.get(
        app_label="users",
        model="user",
    )

    platform_codenames = {
        codename
        for permission_codenames in ROLE_PERMISSIONS.values()
        for codename in permission_codenames
    }

    platform_permissions = Permission.objects.filter(
        content_type=user_content_type,
        codename__in=platform_codenames,
    )

    for role_name in ROLE_PERMISSIONS:
        group = Group.objects.get(
            name=role_name,
        )

        group.permissions.remove(
            *platform_permissions
        )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_create_permission_catalog"),
    ]

    operations = [
        migrations.RunPython(
            assign_role_permissions,
            reverse_code=remove_role_permissions,
        ),
    ]
