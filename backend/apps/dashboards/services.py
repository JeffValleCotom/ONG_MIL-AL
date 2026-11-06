from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from rest_framework import exceptions, serializers

from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    Student,
    StudentIntervention,
    StudentInterventionFollowUp,
    StudentInterventionPlan,
)
from apps.therapy.models import TherapyFollowUp


DASHBOARD_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
}


PROFESSIONAL_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
}


VISIBLE_AREAS_BY_CONTEXT = {
    "DOCENTE": (
        "academic",
        "evaluations",
    ),
    "PSICOLOGO": (
        "psychological",
        "evaluations",
        "interventions",
    ),
    "TERAPEUTA": (
        "therapy",
        "evaluations",
        "interventions",
    ),
    "RESPONSABLE_INSTITUCIONAL": (
        "academic",
        "psychological",
        "therapy",
        "evaluations",
        "interventions",
    ),
}


def resolve_dashboard_context(
    user,
    requested_context="",
):
    user_roles = set(
        user.groups.filter(
            name__in=DASHBOARD_CONTEXTS,
        ).values_list(
            "name",
            flat=True,
        )
    )

    requested_context = (
        requested_context or ""
    ).strip().upper()

    if requested_context:
        if requested_context not in DASHBOARD_CONTEXTS:
            raise serializers.ValidationError(
                {
                    "context": (
                        "El contexto de acceso no es válido."
                    )
                }
            )

        if requested_context not in user_roles:
            raise exceptions.PermissionDenied(
                "No tiene acceso al contexto solicitado."
            )

        return requested_context

    if len(user_roles) == 1:
        return next(iter(user_roles))

    if len(user_roles) > 1:
        raise serializers.ValidationError(
            {
                "context": (
                    "Debe indicar el contexto de acceso "
                    "cuando el usuario posee varios roles."
                )
            }
        )

    raise exceptions.PermissionDenied(
        "No tiene un contexto autorizado "
        "para consultar el dashboard."
    )


def get_dashboard_students(
    user,
    context,
):
    queryset = Student.objects.all()

    if context == "RESPONSABLE_INSTITUCIONAL":
        return queryset

    if context in PROFESSIONAL_CONTEXTS:
        return queryset.filter(
            professional_assignments__professional=user,
            professional_assignments__professional_role=context,
            professional_assignments__is_active=True,
        ).distinct()

    return queryset.none()


def _filter_period(
    queryset,
    date_field,
    date_from=None,
    date_to=None,
):
    filters = {}

    if date_from:
        filters[f"{date_field}__gte"] = date_from

    if date_to:
        filters[f"{date_field}__lte"] = date_to

    if filters:
        queryset = queryset.filter(**filters)

    return queryset


def _monthly_counts(
    queryset,
    date_field,
):
    rows = (
        queryset
        .annotate(
            month=TruncMonth(date_field)
        )
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    result = {}

    for row in rows:
        month = row["month"]

        if month is None:
            continue

        result[month.strftime("%Y-%m")] = row["total"]

    return result


def _merge_timeline(series):
    months = sorted(
        {
            month
            for values in series.values()
            for month in values
        }
    )

    return [
        {
            "period": month,
            **{
                area: values.get(month, 0)
                for area, values in series.items()
            },
        }
        for month in months
    ]


def _build_intervention_indicators(
    user,
    context,
    student_ids,
    date_from,
    date_to,
):
    plans = StudentInterventionPlan.objects.filter(
        student_id__in=student_ids,
    )

    direct_records = StudentIntervention.objects.filter(
        student_id__in=student_ids,
    )

    if context in {
        "PSICOLOGO",
        "TERAPEUTA",
    }:
        plans = plans.filter(
            Q(
                created_by=user,
                professional_role=context,
            )
            | Q(
                responsible=user,
                responsible_role=context,
            )
        ).distinct()

        direct_records = direct_records.filter(
            created_by=user,
            professional_role=context,
        )

    plans_in_period = _filter_period(
        plans,
        "estimated_start_date",
        date_from,
        date_to,
    )

    direct_records = _filter_period(
        direct_records,
        "intervention_date",
        date_from,
        date_to,
    )

    followups = (
        StudentInterventionFollowUp.objects
        .filter(
            intervention_plan__in=plans,
        )
    )

    followups = _filter_period(
        followups,
        "followup_date",
        date_from,
        date_to,
    )

    status_counts = {
        status: plans_in_period.filter(
            status=status
        ).count()
        for status in (
            StudentInterventionPlan.Status.PLANNED,
            StudentInterventionPlan.Status.IN_PROGRESS,
            StudentInterventionPlan.Status.COMPLETED,
            StudentInterventionPlan.Status.CANCELLED,
        )
    }

    direct_series = _monthly_counts(
        direct_records,
        "intervention_date",
    )

    followup_series = _monthly_counts(
        followups,
        "followup_date",
    )

    intervention_months = (
        set(direct_series)
        | set(followup_series)
    )

    combined_series = {
        month: (
            direct_series.get(month, 0)
            + followup_series.get(month, 0)
        )
        for month in intervention_months
    }

    return (
        {
            "plans": plans_in_period.count(),
            "planned": status_counts[
                StudentInterventionPlan.Status.PLANNED
            ],
            "in_progress": status_counts[
                StudentInterventionPlan.Status.IN_PROGRESS
            ],
            "completed": status_counts[
                StudentInterventionPlan.Status.COMPLETED
            ],
            "cancelled": status_counts[
                StudentInterventionPlan.Status.CANCELLED
            ],
            "direct_records": direct_records.count(),
            "followups": followups.count(),
        },
        combined_series,
    )


def build_dashboard_overview(
    user,
    context,
    date_from=None,
    date_to=None,
):
    students = get_dashboard_students(
        user,
        context,
    )

    student_ids = students.values_list(
        "id",
        flat=True,
    )

    visible_areas = VISIBLE_AREAS_BY_CONTEXT[
        context
    ]

    indicators = {}
    timeline_series = {}

    if "academic" in visible_areas:
        academic = AcademicFollowUp.objects.filter(
            student_id__in=student_ids,
        )

        academic = _filter_period(
            academic,
            "followup_date",
            date_from,
            date_to,
        )

        indicators["academic"] = academic.count()

        timeline_series["academic"] = (
            _monthly_counts(
                academic,
                "followup_date",
            )
        )

    if "psychological" in visible_areas:
        psychological = (
            PsychologicalFollowUp.objects.filter(
                student_id__in=student_ids,
            )
        )

        psychological = _filter_period(
            psychological,
            "followup_date",
            date_from,
            date_to,
        )

        indicators["psychological"] = (
            psychological.count()
        )

        timeline_series["psychological"] = (
            _monthly_counts(
                psychological,
                "followup_date",
            )
        )

    if "therapy" in visible_areas:
        therapy = TherapyFollowUp.objects.filter(
            student_id__in=student_ids,
        )

        therapy = _filter_period(
            therapy,
            "followup_date",
            date_from,
            date_to,
        )

        indicators["therapy"] = therapy.count()

        timeline_series["therapy"] = (
            _monthly_counts(
                therapy,
                "followup_date",
            )
        )

    if "evaluations" in visible_areas:
        evaluations = Evaluation.objects.filter(
            student_id__in=student_ids,
        )

        if context in PROFESSIONAL_CONTEXTS:
            evaluations = evaluations.filter(
                professional_role=context,
            )

        evaluations = _filter_period(
            evaluations,
            "evaluation_date",
            date_from,
            date_to,
        )

        indicators["evaluations"] = (
            evaluations.count()
        )

        timeline_series["evaluations"] = (
            _monthly_counts(
                evaluations,
                "evaluation_date",
            )
        )

    if "interventions" in visible_areas:
        (
            intervention_indicators,
            intervention_series,
        ) = _build_intervention_indicators(
            user,
            context,
            student_ids,
            date_from,
            date_to,
        )

        indicators["interventions"] = (
            intervention_indicators
        )

        timeline_series["interventions"] = (
            intervention_series
        )

    activity_total = 0

    for key, value in indicators.items():
        if key == "interventions":
            activity_total += (
                value["direct_records"]
                + value["followups"]
            )
            continue

        activity_total += value

    return {
        "context": context,
        "period": {
            "date_from": date_from,
            "date_to": date_to,
        },
        "visible_areas": visible_areas,
        "students": {
            "total": students.count(),
            "active": students.filter(
                is_active=True,
            ).count(),
            "inactive": students.filter(
                is_active=False,
            ).count(),
        },
        "activity": {
            "total_records": activity_total,
            "indicators": indicators,
        },
        "timeline": _merge_timeline(
            timeline_series
        ),
    }
