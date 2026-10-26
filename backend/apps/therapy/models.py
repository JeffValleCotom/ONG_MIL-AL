from django.conf import settings
from django.db import models


class TherapyFollowUp(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="therapy_followups",
    )

    followup_date = models.DateField()

    therapy_area = models.CharField(
        max_length=120,
    )

    objectives = models.TextField()

    activities = models.TextField(
        blank=True,
    )

    progress_notes = models.TextField()

    recommendations = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="therapy_followups_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="therapy_followups_updated",
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
                name="therapy_student_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.therapy_area} - "
            f"{self.followup_date}"
        )