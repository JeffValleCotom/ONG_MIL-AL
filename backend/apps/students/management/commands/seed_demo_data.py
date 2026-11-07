from django.core.management.base import BaseCommand

from apps.students.demo_data import (
    DEMO_STUDENT_PREFIX,
    DEMO_USERNAMES,
    seed_demo_data,
)


class Command(BaseCommand):
    help = (
        "Crea un conjunto idempotente de datos ficticios "
        "para demostrar las funciones de MIL-AL."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            required=True,
            help=(
                "Contraseña temporal de los usuarios demo. "
                "Debe proporcionarse explícitamente."
            ),
        )

    def handle(self, *args, **options):
        password = options["password"]

        result = seed_demo_data(password=password)

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de demostración creados correctamente."
            )
        )

        self.stdout.write(
            f"Usuarios demo: {result['users']}"
        )
        self.stdout.write(
            f"Estudiantes demo: {result['students']}"
        )
        self.stdout.write(
            f"Prefijo estudiantes: {DEMO_STUDENT_PREFIX}"
        )

        self.stdout.write("")
        self.stdout.write("Usuarios disponibles:")

        for username in DEMO_USERNAMES.values():
            self.stdout.write(f"  - {username}")

        self.stdout.write("")
        self.stdout.write(
            "La contraseña es la indicada mediante --password."
        )
