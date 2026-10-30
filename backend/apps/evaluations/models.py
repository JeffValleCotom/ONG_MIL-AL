from django.conf import settings
from django.db import models

from apps.students.models import (
    StudentProfessionalAssignment,
)


class Evaluation(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="evaluations",
    )

    evaluation_date = models.DateField()

    evaluation_type = models.CharField(
        max_length=120,
    )

    results = models.TextField()

    observations = models.TextField(
        blank=True,
    )

    professional_role = models.CharField(
        max_length=20,
        choices=(
            StudentProfessionalAssignment
            .ProfessionalRole
            .choices
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evaluations_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evaluations_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-evaluation_date",
            "-created_at",
            "-id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "evaluation_date",
                ],
                name="evaluation_student_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.evaluation_type} - "
            f"{self.evaluation_date}"
        )
