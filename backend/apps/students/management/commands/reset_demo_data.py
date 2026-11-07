from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from apps.students.demo_data import (
    get_demo_counts,
    reset_demo_data,
)


CONFIRMATION = "RESET-DEMO-DATA"


class Command(BaseCommand):
    help = (
        "Elimina únicamente los datos creados por "
        "seed_demo_data, incluidos sus documentos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            default="",
            help=(
                "Para ejecutar la eliminación debe ser "
                f"exactamente {CONFIRMATION}."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Muestra qué datos demo serían eliminados "
                "sin modificar la base de datos."
            ),
        )

    def handle(self, *args, **options):
        counts = get_demo_counts()

        self.stdout.write(
            "Datos demo detectados:"
        )

        for key, value in counts.items():
            self.stdout.write(
                f"  {key}: {value}"
            )

        if options["dry_run"]:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN: no se modificó ningún dato."
                )
            )
            return

        if options["confirm"] != CONFIRMATION:
            raise CommandError(
                "Confirmación requerida. "
                "Ejecute nuevamente con "
                f"--confirm {CONFIRMATION}"
            )

        result = reset_demo_data()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Datos de demostración eliminados."
            )
        )

        if result["blob_errors"]:
            self.stdout.write(
                self.style.WARNING(
                    "La base de datos quedó limpia, pero "
                    "algunos archivos no pudieron eliminarse:"
                )
            )

            for error in result["blob_errors"]:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - {error}"
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Documentos demo eliminados del almacenamiento."
                )
            )
