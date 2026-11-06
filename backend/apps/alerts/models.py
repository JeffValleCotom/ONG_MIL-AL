from django.conf import settings
from django.db import models

from apps.students.models import (
    Student,
    StudentIntervention,
    StudentInterventionPlan,
)


class Alert(models.Model):
    class Condition(models.TextChoices):
        INTERVENTION_OVERDUE = (
            "INTERVENTION_OVERDUE",
            "Plan de intervención vencido",
        )
        INTERVENTION_START_DELAYED = (
            "INTERVENTION_START_DELAYED",
            "Inicio de intervención pendiente",
        )

    class Status(models.TextChoices):
        OPEN = "OPEN", "Pendiente"
        REVIEWED = "REVIEWED", "Revisada"
        RESOLVED = "RESOLVED", "Resuelta"

    condition = models.CharField(
        max_length=50,
        choices=Condition.choices,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="alerts",
    )

    intervention_plan = models.ForeignKey(
        StudentInterventionPlan,
        on_delete=models.PROTECT,
        related_name="alerts",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_alerts",
    )

    assigned_role = models.CharField(
        max_length=20,
        choices=StudentIntervention.ProfessionalRole.choices,
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    detected_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_alerts",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )

    resolved_at = models.DateTimeField(
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
            "status",
            "-updated_at",
            "-id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "condition",
                    "intervention_plan",
                ],
                name="alert_condition_plan_uniq",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "assigned_to",
                    "assigned_role",
                    "status",
                ],
                name="alert_assignee_status_idx",
            ),
            models.Index(
                fields=[
                    "student",
                    "status",
                ],
                name="alert_student_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.condition} - "
            f"{self.status}"
        )


class AlertEvent(models.Model):
    class EventType(models.TextChoices):
        CREATED = "CREATED", "Creada"
        REVIEWED = "REVIEWED", "Revisada"
        RESOLVED = "RESOLVED", "Resuelta"
        REOPENED = "REOPENED", "Reabierta"
        REASSIGNED = "REASSIGNED", "Reasignada"

    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name="history",
    )

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
    )

    from_status = models.CharField(
        max_length=20,
        choices=Alert.Status.choices,
        null=True,
        blank=True,
    )

    to_status = models.CharField(
        max_length=20,
        choices=Alert.Status.choices,
        null=True,
        blank=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alert_events",
    )

    note = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "created_at",
            "id",
        ]

    def __str__(self):
        return (
            f"Alerta {self.alert_id} - "
            f"{self.event_type}"
        )
