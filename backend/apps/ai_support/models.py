from django.conf import settings
from django.db import models


class AIInsight(models.Model):
    class Kind(models.TextChoices):
        ANALYSIS = (
            "ANALYSIS",
            "Análisis inteligente",
        )
        FOLLOWUP_SUGGESTION = (
            "FOLLOWUP_SUGGESTION",
            "Sugerencia de seguimiento",
        )
        INTERVENTION_RECOMMENDATION = (
            "INTERVENTION_RECOMMENDATION",
            "Recomendación de intervención",
        )
        REPORT_SUGGESTION = (
            "REPORT_SUGGESTION",
            "Sugerencia para reporte",
        )

    class ReviewStatus(models.TextChoices):
        NOT_APPLICABLE = (
            "NOT_APPLICABLE",
            "No aplica",
        )
        PENDING = (
            "PENDING",
            "Pendiente",
        )
        ACCEPTED = (
            "ACCEPTED",
            "Aceptada",
        )
        DISCARDED = (
            "DISCARDED",
            "Descartada",
        )
        IGNORED = (
            "IGNORED",
            "Ignorada",
        )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="ai_insights",
    )

    source_report = models.ForeignKey(
        "reports.StudentReport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_insights",
    )

    kind = models.CharField(
        max_length=40,
        choices=Kind.choices,
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

    context_snapshot = models.JSONField()

    result_json = models.JSONField()

    provider = models.CharField(
        max_length=40,
    )
    model_name = models.CharField(
        max_length=120,
    )
    provider_response_id = models.CharField(
        max_length=200,
        blank=True,
    )

    usage_json = models.JSONField(
        null=True,
        blank=True,
    )
    prompt_version = models.CharField(
        max_length=40,
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="generated_ai_insights",
    )

    review_status = models.CharField(
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.NOT_APPLICABLE,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_ai_insights",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    professional_notes = models.TextField(
        blank=True,
    )

    edited_content = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
            "-id",
        ]
        indexes = [
            models.Index(
                fields=[
                    "student",
                    "kind",
                    "created_at",
                ],
                name="ai_student_kind_date_idx",
            ),
            models.Index(
                fields=[
                    "generated_by",
                    "generated_role",
                ],
                name="ai_creator_role_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} "
            f"- {self.kind} "
            f"- {self.created_at:%Y-%m-%d}"
        )
