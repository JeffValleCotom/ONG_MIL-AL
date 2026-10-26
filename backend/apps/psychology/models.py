from django.conf import settings
from django.db import models


class PsychologicalFollowUp(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="psychological_followups",
    )

    followup_date = models.DateField()

    reason = models.CharField(
        max_length=200,
    )

    observations = models.TextField()

    emotional_behavioral_notes = models.TextField(
        blank=True,
    )

    recommendations = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="psychological_followups_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="psychological_followups_updated",
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
                name="psych_student_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.reason} - "
            f"{self.followup_date}"
        )
