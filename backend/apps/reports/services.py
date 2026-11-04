from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    StudentIntervention,
    StudentInterventionPlan,
)
from apps.therapy.models import TherapyFollowUp

from .models import StudentReport


def _date_value(value):
    return value.isoformat() if value else None


def _user_value(user):
    if not user:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def _student_value(student):
    return {
        "id": student.id,
        "institutional_code": student.institutional_code,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "date_of_birth": _date_value(
            student.date_of_birth
        ),
        "admission_date": _date_value(
            student.admission_date
        ),
        "is_active": student.is_active,
    }


def _apply_date_filter(
    queryset,
    field,
    date_from,
    date_to,
):
    filters = {}

    if date_from:
        filters[f"{field}__gte"] = date_from

    if date_to:
        filters[f"{field}__lte"] = date_to

    if filters:
        queryset = queryset.filter(**filters)

    return queryset


def _academic_items(
    student,
    date_from,
    date_to,
):
    queryset = AcademicFollowUp.objects.filter(
        student=student,
    ).select_related(
        "created_by",
    )

    queryset = _apply_date_filter(
        queryset,
        "followup_date",
        date_from,
        date_to,
    )

    return [
        {
            "id": item.id,
            "date": _date_value(
                item.followup_date
            ),
            "academic_period": item.academic_period,
            "subject": item.subject,
            "observations": item.observations,
            "strengths": item.strengths,
            "areas_for_improvement": (
                item.areas_for_improvement
            ),
            "recommendations": item.recommendations,
            "responsible": _user_value(
                item.created_by
            ),
        }
        for item in queryset
    ]


def _psychological_items(
    student,
    date_from,
    date_to,
):
    queryset = PsychologicalFollowUp.objects.filter(
        student=student,
    ).select_related(
        "created_by",
    )

    queryset = _apply_date_filter(
        queryset,
        "followup_date",
        date_from,
        date_to,
    )

    return [
        {
            "id": item.id,
            "date": _date_value(
                item.followup_date
            ),
            "reason": item.reason,
            "observations": item.observations,
            "emotional_behavioral_notes": (
                item.emotional_behavioral_notes
            ),
            "recommendations": item.recommendations,
            "responsible": _user_value(
                item.created_by
            ),
        }
        for item in queryset
    ]


def _therapy_items(
    student,
    date_from,
    date_to,
):
    queryset = TherapyFollowUp.objects.filter(
        student=student,
    ).select_related(
        "created_by",
    )

    queryset = _apply_date_filter(
        queryset,
        "followup_date",
        date_from,
        date_to,
    )

    return [
        {
            "id": item.id,
            "date": _date_value(
                item.followup_date
            ),
            "therapy_area": item.therapy_area,
            "objectives": item.objectives,
            "activities": item.activities,
            "progress_notes": item.progress_notes,
            "recommendations": item.recommendations,
            "responsible": _user_value(
                item.created_by
            ),
        }
        for item in queryset
    ]


def _evaluation_items(
    student,
    date_from,
    date_to,
):
    queryset = Evaluation.objects.filter(
        student=student,
    ).select_related(
        "created_by",
    )

    queryset = _apply_date_filter(
        queryset,
        "evaluation_date",
        date_from,
        date_to,
    )

    return [
        {
            "id": item.id,
            "date": _date_value(
                item.evaluation_date
            ),
            "evaluation_type": item.evaluation_type,
            "results": item.results,
            "observations": item.observations,
            "professional_role": (
                item.professional_role
            ),
            "responsible": _user_value(
                item.created_by
            ),
        }
        for item in queryset
    ]


def _performed_interventions(
    student,
    date_from,
    date_to,
):
    queryset = StudentIntervention.objects.filter(
        student=student,
    ).select_related(
        "created_by",
    )

    queryset = _apply_date_filter(
        queryset,
        "intervention_date",
        date_from,
        date_to,
    )

    return [
        {
            "id": item.id,
            "date": _date_value(
                item.intervention_date
            ),
            "professional_role": (
                item.professional_role
            ),
            "objectives": item.objectives,
            "observations": item.observations,
            "responsible": _user_value(
                item.created_by
            ),
        }
        for item in queryset
    ]


def _planned_interventions(
    student,
    date_from,
    date_to,
):
    queryset = (
        StudentInterventionPlan.objects
        .filter(
            student=student,
        )
        .select_related(
            "responsible",
            "created_by",
        )
        .prefetch_related(
            "followups__created_by",
        )
    )

    if date_from:
        queryset = queryset.filter(
            estimated_start_date__gte=date_from,
        )

    if date_to:
        queryset = queryset.filter(
            estimated_start_date__lte=date_to,
        )

    result = []

    for plan in queryset:
        result.append(
            {
                "id": plan.id,
                "objectives": plan.objectives,
                "estimated_start_date": (
                    _date_value(
                        plan.estimated_start_date
                    )
                ),
                "estimated_end_date": (
                    _date_value(
                        plan.estimated_end_date
                    )
                ),
                "status": plan.status,
                "professional_role": (
                    plan.professional_role
                ),
                "responsible_role": (
                    plan.responsible_role
                ),
                "responsible": _user_value(
                    plan.responsible
                ),
                "followups": [
                    {
                        "id": followup.id,
                        "date": _date_value(
                            followup.followup_date
                        ),
                        "progress": followup.progress,
                        "results": followup.results,
                        "observations": (
                            followup.observations
                        ),
                        "status": followup.status,
                        "responsible": _user_value(
                            followup.created_by
                        ),
                    }
                    for followup in plan.followups.all()
                ],
            }
        )

    return result


def build_report_snapshot(
    *,
    student,
    report_type,
    date_from=None,
    date_to=None,
):
    base = {
        "student": _student_value(
            student
        ),
        "report_type": report_type,
        "period": {
            "date_from": _date_value(
                date_from
            ),
            "date_to": _date_value(
                date_to
            ),
        },
    }

    if report_type == StudentReport.ReportType.GENERAL:
        base["sections"] = {
            "general": _student_value(student),
        }

        return base

    if report_type == StudentReport.ReportType.ACADEMIC:
        items = _academic_items(
            student,
            date_from,
            date_to,
        )

        base["sections"] = {
            "academic": items,
        }

        base["summary"] = {
            "total_records": len(items),
        }

        return base

    if (
        report_type
        == StudentReport.ReportType.PSYCHOLOGICAL
    ):
        items = _psychological_items(
            student,
            date_from,
            date_to,
        )

        base["sections"] = {
            "psychological": items,
        }

        base["summary"] = {
            "total_records": len(items),
        }

        return base

    if report_type == StudentReport.ReportType.THERAPY:
        items = _therapy_items(
            student,
            date_from,
            date_to,
        )

        base["sections"] = {
            "therapy": items,
        }

        base["summary"] = {
            "total_records": len(items),
        }

        return base

    if (
        report_type
        == StudentReport.ReportType.INTERVENTIONS
    ):
        performed = _performed_interventions(
            student,
            date_from,
            date_to,
        )

        planned = _planned_interventions(
            student,
            date_from,
            date_to,
        )

        base["sections"] = {
            "performed_interventions": performed,
            "planned_interventions": planned,
        }

        base["summary"] = {
            "performed_count": len(performed),
            "planned_count": len(planned),
        }

        return base

    if report_type == StudentReport.ReportType.INTEGRAL:
        academic = _academic_items(
            student,
            date_from,
            date_to,
        )

        psychological = _psychological_items(
            student,
            date_from,
            date_to,
        )

        therapy = _therapy_items(
            student,
            date_from,
            date_to,
        )

        evaluations = _evaluation_items(
            student,
            date_from,
            date_to,
        )

        performed = _performed_interventions(
            student,
            date_from,
            date_to,
        )

        planned = _planned_interventions(
            student,
            date_from,
            date_to,
        )

        highlights = []

        for item in academic:
            if item["strengths"]:
                highlights.append(
                    {
                        "area": "ACADEMIC",
                        "text": item["strengths"],
                    }
                )

        for item in therapy:
            if item["progress_notes"]:
                highlights.append(
                    {
                        "area": "THERAPY",
                        "text": item["progress_notes"],
                    }
                )

        for plan in planned:
            for followup in plan["followups"]:
                if followup["progress"]:
                    highlights.append(
                        {
                            "area": "INTERVENTIONS",
                            "text": followup["progress"],
                        }
                    )

        base["sections"] = {
            "academic": academic,
            "psychological": psychological,
            "therapy": therapy,
            "evaluations": evaluations,
            "performed_interventions": performed,
            "planned_interventions": planned,
        }

        base["summary"] = {
            "academic_count": len(academic),
            "psychological_count": len(
                psychological
            ),
            "therapy_count": len(therapy),
            "evaluation_count": len(evaluations),
            "performed_intervention_count": len(
                performed
            ),
            "planned_intervention_count": len(
                planned
            ),
            "highlights": highlights[:10],
        }

        return base

    raise ValueError(
        "Tipo de reporte no soportado."
    )
