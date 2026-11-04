from django.conf import settings
from django.db import models

from apps.students.models import Student


class StudentReport(models.Model):
    class ReportType(models.TextChoices):
        GENERAL = "GENERAL", "General"
        ACADEMIC = "ACADEMIC", "Académico"
        PSYCHOLOGICAL = "PSYCHOLOGICAL", "Psicológico"
        THERAPY = "THERAPY", "Terapéutico"
        INTERVENTIONS = "INTERVENTIONS", "Intervenciones"
        INTEGRAL = "INTEGRAL", "Integral"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="reports",
    )

    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
    )

    date_from = models.DateField(
        null=True,
        blank=True,
    )

    date_to = models.DateField(
        null=True,
        blank=True,
    )

    generated_role = models.CharField(
        max_length=40,
    )

    content_snapshot = models.JSONField()

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_reports_generated",
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-generated_at",
            "-id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "report_type",
                    "generated_at",
                ],
                name="report_student_type_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.report_type} - "
            f"{self.generated_at:%Y-%m-%d}"
        )
