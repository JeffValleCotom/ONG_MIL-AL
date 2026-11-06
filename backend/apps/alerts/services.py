from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from apps.students.models import (
    StudentInterventionPlan,
)

from .models import Alert, AlertEvent


ALERT_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
}


PROFESSIONAL_ALERT_CONTEXTS = {
    "PSICOLOGO",
    "TERAPEUTA",
}


def resolve_alert_context(
    user,
    requested_context="",
):
    user_roles = set(
        user.groups.filter(
            name__in=ALERT_CONTEXTS,
        ).values_list(
            "name",
            flat=True,
        )
    )

    if not user_roles:
        raise exceptions.PermissionDenied(
            "No posee un contexto autorizado "
            "para consultar alertas."
        )

    requested_context = (
        requested_context
        or ""
    ).strip().upper()

    if requested_context:
        if requested_context not in ALERT_CONTEXTS:
            raise exceptions.ValidationError({
                "context": (
                    "El contexto solicitado "
                    "no es válido."
                )
            })

        if requested_context not in user_roles:
            raise exceptions.PermissionDenied(
                "No posee el contexto solicitado."
            )

        return requested_context

    if len(user_roles) > 1:
        raise exceptions.ValidationError({
            "context": (
                "Debe indicar el contexto "
                "de trabajo."
            )
        })

    return next(iter(user_roles))


def get_alert_queryset(
    user,
    context,
):
    queryset = (
        Alert.objects
        .select_related(
            "student",
            "intervention_plan",
            "assigned_to",
            "reviewed_by",
            "resolved_by",
        )
        .prefetch_related(
            "history__performed_by",
        )
    )

    if context == "RESPONSABLE_INSTITUCIONAL":
        return queryset

    if context in PROFESSIONAL_ALERT_CONTEXTS:
        return queryset.filter(
            assigned_to=user,
            assigned_role=context,
        )

    return queryset.none()


def _get_plan_queryset(
    user,
    context,
):
    queryset = (
        StudentInterventionPlan.objects
        .select_related(
            "student",
            "responsible",
        )
    )

    if context == "RESPONSABLE_INSTITUCIONAL":
        return queryset

    if context in PROFESSIONAL_ALERT_CONTEXTS:
        return queryset.filter(
            responsible=user,
            responsible_role=context,
        )

    return queryset.none()


def _get_active_condition(
    plan,
    today,
):
    if plan.status in (
        StudentInterventionPlan.Status.COMPLETED,
        StudentInterventionPlan.Status.CANCELLED,
    ):
        return None

    if (
        plan.estimated_end_date
        and plan.estimated_end_date < today
    ):
        return Alert.Condition.INTERVENTION_OVERDUE

    if (
        plan.status
        == StudentInterventionPlan.Status.PLANNED
        and plan.estimated_start_date < today
    ):
        return (
            Alert.Condition
            .INTERVENTION_START_DELAYED
        )

    return None


def _build_reason(
    plan,
    condition,
):
    if (
        condition
        == Alert.Condition.INTERVENTION_OVERDUE
    ):
        return (
            "El plan de intervención alcanzó "
            "su fecha estimada de finalización "
            f"({plan.estimated_end_date}) y "
            "continúa pendiente de cierre."
        )

    return (
        "La fecha estimada de inicio del plan "
        f"({plan.estimated_start_date}) ya pasó "
        "y la intervención continúa planificada."
    )


def _create_event(
    alert,
    event_type,
    *,
    from_status=None,
    to_status=None,
    performed_by=None,
    note="",
):
    return AlertEvent.objects.create(
        alert=alert,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        performed_by=performed_by,
        note=note,
    )


def _resolve_alert(
    alert,
    now,
):
    if alert.status == Alert.Status.RESOLVED:
        return

    previous_status = alert.status

    alert.status = Alert.Status.RESOLVED
    alert.resolved_at = now
    alert.resolved_by = None

    alert.save(
        update_fields=[
            "status",
            "resolved_at",
            "resolved_by",
            "updated_at",
        ]
    )

    _create_event(
        alert,
        AlertEvent.EventType.RESOLVED,
        from_status=previous_status,
        to_status=Alert.Status.RESOLVED,
        note=(
            "La condición operativa que originó "
            "la alerta dejó de cumplirse."
        ),
    )


@transaction.atomic
def sync_operational_alerts(
    user,
    context,
):
    today = timezone.localdate()
    now = timezone.now()

    plans = _get_plan_queryset(
        user,
        context,
    )

    for plan in plans.iterator():
        active_condition = _get_active_condition(
            plan,
            today,
        )

        active_alerts = (
            Alert.objects
            .filter(
                intervention_plan=plan,
            )
            .exclude(
                status=Alert.Status.RESOLVED,
            )
        )

        if active_condition:
            active_alerts = active_alerts.exclude(
                condition=active_condition,
            )

        for obsolete_alert in active_alerts:
            _resolve_alert(
                obsolete_alert,
                now,
            )

        if not active_condition:
            continue

        reason = _build_reason(
            plan,
            active_condition,
        )

        alert, created = Alert.objects.get_or_create(
            intervention_plan=plan,
            condition=active_condition,
            defaults={
                "student": plan.student,
                "assigned_to": plan.responsible,
                "assigned_role": (
                    plan.responsible_role
                ),
                "reason": reason,
                "status": Alert.Status.OPEN,
            },
        )

        if created:
            _create_event(
                alert,
                AlertEvent.EventType.CREATED,
                to_status=Alert.Status.OPEN,
                note=reason,
            )
            continue

        update_fields = []

        if alert.student_id != plan.student_id:
            alert.student = plan.student
            update_fields.append("student")

        if alert.reason != reason:
            alert.reason = reason
            update_fields.append("reason")

        assignee_changed = (
            alert.assigned_to_id
            != plan.responsible_id
            or alert.assigned_role
            != plan.responsible_role
        )

        if assignee_changed:
            alert.assigned_to = plan.responsible
            alert.assigned_role = (
                plan.responsible_role
            )

            update_fields.extend([
                "assigned_to",
                "assigned_role",
            ])

        if alert.status == Alert.Status.RESOLVED:
            previous_status = alert.status

            alert.status = Alert.Status.OPEN
            alert.reviewed_by = None
            alert.reviewed_at = None
            alert.resolved_by = None
            alert.resolved_at = None

            update_fields.extend([
                "status",
                "reviewed_by",
                "reviewed_at",
                "resolved_by",
                "resolved_at",
            ])

            alert.save(
                update_fields=[
                    *dict.fromkeys(update_fields),
                    "updated_at",
                ]
            )

            _create_event(
                alert,
                AlertEvent.EventType.REOPENED,
                from_status=previous_status,
                to_status=Alert.Status.OPEN,
                note=(
                    "La condición operativa volvió "
                    "a cumplirse."
                ),
            )

            if assignee_changed:
                _create_event(
                    alert,
                    AlertEvent.EventType.REASSIGNED,
                    performed_by=None,
                    note=(
                        "La responsabilidad del plan "
                        "fue actualizada."
                    ),
                )

            continue

        if update_fields:
            alert.save(
                update_fields=[
                    *dict.fromkeys(update_fields),
                    "updated_at",
                ]
            )

        if assignee_changed:
            _create_event(
                alert,
                AlertEvent.EventType.REASSIGNED,
                note=(
                    "La responsabilidad del plan "
                    "fue actualizada."
                ),
            )
