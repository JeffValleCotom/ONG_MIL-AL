from django.db import migrations


PLATFORM_PERMISSIONS = (
    (
        "manage_users",
        "Puede administrar usuarios institucionales",
    ),
    (
        "manage_roles",
        "Puede administrar roles institucionales",
    ),
    (
        "manage_permissions",
        "Puede administrar permisos institucionales",
    ),
    (
        "view_students",
        "Puede consultar información general de estudiantes",
    ),
    (
        "manage_students",
        "Puede administrar información general de estudiantes",
    ),
    (
        "view_academic_followups",
        "Puede consultar seguimientos académicos",
    ),
    (
        "manage_academic_followups",
        "Puede administrar seguimientos académicos",
    ),
    (
        "view_psychological_followups",
        "Puede consultar seguimientos psicológicos",
    ),
    (
        "manage_psychological_followups",
        "Puede administrar seguimientos psicológicos",
    ),
    (
        "view_interventions",
        "Puede consultar intervenciones",
    ),
    (
        "manage_interventions",
        "Puede administrar intervenciones",
    ),
    (
        "view_reports",
        "Puede consultar reportes autorizados",
    ),
    (
        "view_dashboard",
        "Puede consultar paneles e indicadores autorizados",
    ),
    (
        "view_alerts",
        "Puede consultar alertas autorizadas",
    ),
    (
        "use_ai_assistant",
        "Puede utilizar el asistente de inteligencia artificial",
    ),
    (
        "view_audit",
        "Puede consultar información de auditoría",
    ),
)


def create_permission_catalog(apps, schema_editor):
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
    )
    Permission = apps.get_model(
        "auth",
        "Permission",
    )

    user_content_type, _ = ContentType.objects.get_or_create(
        app_label="users",
        model="user",
    )

    for codename, name in PLATFORM_PERMISSIONS:
        Permission.objects.update_or_create(
            content_type=user_content_type,
            codename=codename,
            defaults={
                "name": name,
            },
        )


def remove_permission_catalog(apps, schema_editor):
    ContentType = apps.get_model(
        "contenttypes",
        "ContentType",
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

    permission_codenames = [
        codename
        for codename, _ in PLATFORM_PERMISSIONS
    ]

    Permission.objects.filter(
        content_type=user_content_type,
        codename__in=permission_codenames,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_create_initial_roles"),
    ]

    operations = [
        migrations.RunPython(
            create_permission_catalog,
            reverse_code=remove_permission_catalog,
        ),
    ]
