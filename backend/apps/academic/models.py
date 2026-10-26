from django.conf import settings
from django.db import models


class AcademicFollowUp(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="academic_followups",
    )

    followup_date = models.DateField()

    academic_period = models.CharField(
        max_length=50,
    )

    subject = models.CharField(
        max_length=120,
    )

    observations = models.TextField()

    strengths = models.TextField(
        blank=True,
    )

    areas_for_improvement = models.TextField(
        blank=True,
    )

    recommendations = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="academic_followups_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="academic_followups_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-followup_date",
            "-created_at",
            "-id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "followup_date",
                ],
                name="academic_student_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.subject} - "
            f"{self.followup_date}"
        )
