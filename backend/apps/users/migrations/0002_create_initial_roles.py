from django.db import migrations


INITIAL_ROLES = [
    "ADMINISTRADOR",
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
]


def create_initial_roles(apps, schema_editor):
    """
    Crea el catálogo base de roles institucionales.

    Se utiliza get_or_create para que la operación sea idempotente
    y no genere roles duplicados si alguno ya existe.
    """
    Group = apps.get_model("auth", "Group")

    for role_name in INITIAL_ROLES:
        Group.objects.get_or_create(name=role_name)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_roles,
            reverse_code=migrations.RunPython.noop,
        ),
    ]