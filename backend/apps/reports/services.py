from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    StudentIntervention,
    StudentInterventionPlan,
)
from apps.therapy.models import TherapyFollowUp

from .models import StudentReport


ROLE_TEACHER = "DOCENTE"
ROLE_PSYCHOLOGIST = "PSICOLOGO"
ROLE_THERAPIST = "TERAPEUTA"
ROLE_INSTITUTIONAL = "RESPONSABLE_INSTITUCIONAL"


def _date_value(value):
    return value.isoformat() if value else None


def _user_value(user):
    if user is None:
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
    field_name,
    date_from,
    date_to,
):
    if date_from:
        queryset = queryset.filter(
            **{
                f"{field_name}__gte": date_from,
            }
        )

    if date_to:
        queryset = queryset.filter(
            **{
                f"{field_name}__lte": date_to,
            }
        )

    return queryset


def _academic_items(
    student,
    date_from,
    date_to,
    generated_by=None,
    generated_role=None,
):
    queryset = (
        AcademicFollowUp.objects
        .filter(
            student=student,
        )
        .select_related(
            "created_by",
        )
    )

    if generated_by is not None:
        queryset = queryset.filter(
            created_by=generated_by,
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
            "academic_period": (
                item.academic_period
            ),
            "subject": item.subject,
            "observations": (
                item.observations
            ),
            "strengths": item.strengths,
            "areas_for_improvement": (
                item.areas_for_improvement
            ),
            "recommendations": (
                item.recommendations
            ),
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
    generated_by=None,
    generated_role=None,
):
    queryset = (
        PsychologicalFollowUp.objects
        .filter(
            student=student,
        )
        .select_related(
            "created_by",
        )
    )

    if generated_by is not None:
        queryset = queryset.filter(
            created_by=generated_by,
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
            "emotional_behavioral_notes": (
                item.emotional_behavioral_notes
            ),
            "recommendations": (
                item.recommendations
            ),
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
    generated_by=None,
    generated_role=None,
):
    queryset = (
        TherapyFollowUp.objects
        .filter(
            student=student,
        )
        .select_related(
            "created_by",
        )
    )

    if generated_by is not None:
        queryset = queryset.filter(
            created_by=generated_by,
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
            "therapy_area": (
                item.therapy_area
            ),
            "objectives": item.objectives,
            "activities": item.activities,
            "progress_notes": (
                item.progress_notes
            ),
            "recommendations": (
                item.recommendations
            ),
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
    generated_by=None,
    generated_role=None,
):
    queryset = (
        Evaluation.objects
        .filter(
            student=student,
        )
        .select_related(
            "created_by",
        )
    )

    if generated_by is not None:
        queryset = queryset.filter(
            created_by=generated_by,
        )

    if generated_role:
        queryset = queryset.filter(
            professional_role=generated_role,
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
            "evaluation_type": (
                item.evaluation_type
            ),
            "results": item.results,
            "observations": (
                item.observations
            ),
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
    generated_by=None,
    generated_role=None,
):
    queryset = (
        StudentIntervention.objects
        .filter(
            student=student,
        )
        .select_related(
            "created_by",
        )
    )

    if generated_by is not None:
        queryset = queryset.filter(
            created_by=generated_by,
        )

    if generated_role:
        queryset = queryset.filter(
            professional_role=generated_role,
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
            "observations": (
                item.observations
            ),
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
    generated_by=None,
    generated_role=None,
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

    if generated_by is not None:
        queryset = queryset.filter(
            responsible=generated_by,
        )

    if generated_role:
        queryset = queryset.filter(
            responsible_role=generated_role,
        )

    if date_from:
        queryset = queryset.filter(
            estimated_start_date__gte=date_from
        )

    if date_to:
        queryset = queryset.filter(
            estimated_start_date__lte=date_to
        )

    result = []

    for plan in queryset:
        followups = []

        for followup in plan.followups.all():
            if (
                generated_by is not None
                and followup.created_by_id
                != generated_by.id
            ):
                continue

            followups.append(
                {
                    "id": followup.id,
                    "date": _date_value(
                        followup.followup_date
                    ),
                    "progress": (
                        followup.progress
                    ),
                    "results": (
                        followup.results
                    ),
                    "observations": (
                        followup.observations
                    ),
                    "status": (
                        followup.status
                    ),
                    "responsible": (
                        _user_value(
                            followup.created_by
                        )
                    ),
                }
            )

        result.append(
            {
                "id": plan.id,
                "objectives": (
                    plan.objectives
                ),
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
                "followups": followups,
            }
        )

    return result


SUPPORTED_DATA_SECTIONS = {
    "academic": _academic_items,
    "psychological": _psychological_items,
    "therapy": _therapy_items,
    "evaluations": _evaluation_items,
    "performed_interventions": (
        _performed_interventions
    ),
    "planned_interventions": (
        _planned_interventions
    ),
}


INTEGRAL_SECTIONS_BY_ROLE = {
    ROLE_TEACHER: (
        "academic",
        "evaluations",
    ),
    ROLE_PSYCHOLOGIST: (
        "psychological",
        "evaluations",
        "performed_interventions",
        "planned_interventions",
    ),
    ROLE_THERAPIST: (
        "therapy",
        "evaluations",
        "performed_interventions",
        "planned_interventions",
    ),
    ROLE_INSTITUTIONAL: (
        "general",
    ),
}


def build_student_data_sections(
    *,
    student,
    sections,
    generated_by=None,
    generated_role=None,
    date_from=None,
    date_to=None,
):
    unsupported = (
        set(sections)
        - set(SUPPORTED_DATA_SECTIONS)
    )

    if unsupported:
        unsupported_names = ", ".join(
            sorted(unsupported)
        )

        raise ValueError(
            "Secciones de información "
            "no soportadas: "
            f"{unsupported_names}"
        )

    result = {}

    for section in sections:
        builder = (
            SUPPORTED_DATA_SECTIONS[
                section
            ]
        )

        result[section] = builder(
            student,
            date_from,
            date_to,
            generated_by,
            generated_role,
        )

    return result


def _build_integral_sections(
    *,
    student,
    generated_by,
    generated_role,
    date_from,
    date_to,
):
    section_names = (
        INTEGRAL_SECTIONS_BY_ROLE.get(
            generated_role,
            (),
        )
    )

    if (
        generated_role
        == ROLE_INSTITUTIONAL
    ):
        return {
            "general": _student_value(
                student
            ),
        }

    sections = {}

    for section_name in section_names:
        builder = (
            SUPPORTED_DATA_SECTIONS[
                section_name
            ]
        )

        sections[section_name] = builder(
            student,
            date_from,
            date_to,
            generated_by,
            generated_role,
        )

    return sections


def _build_integral_summary(
    *,
    sections,
    generated_role,
):
    summary = {}

    if generated_role == ROLE_TEACHER:
        summary["academic_count"] = len(
            sections.get(
                "academic",
                [],
            )
        )
        summary["evaluation_count"] = len(
            sections.get(
                "evaluations",
                [],
            )
        )

    elif generated_role == ROLE_PSYCHOLOGIST:
        summary["psychological_count"] = len(
            sections.get(
                "psychological",
                [],
            )
        )
        summary["evaluation_count"] = len(
            sections.get(
                "evaluations",
                [],
            )
        )
        summary[
            "performed_intervention_count"
        ] = len(
            sections.get(
                "performed_interventions",
                [],
            )
        )
        summary[
            "planned_intervention_count"
        ] = len(
            sections.get(
                "planned_interventions",
                [],
            )
        )

    elif generated_role == ROLE_THERAPIST:
        summary["therapy_count"] = len(
            sections.get(
                "therapy",
                [],
            )
        )
        summary["evaluation_count"] = len(
            sections.get(
                "evaluations",
                [],
            )
        )
        summary[
            "performed_intervention_count"
        ] = len(
            sections.get(
                "performed_interventions",
                [],
            )
        )
        summary[
            "planned_intervention_count"
        ] = len(
            sections.get(
                "planned_interventions",
                [],
            )
        )

    highlights = []

    for item in sections.get(
        "academic",
        [],
    ):
        if item.get("strengths"):
            highlights.append(
                {
                    "area": "ACADEMIC",
                    "text": (
                        item["strengths"]
                    ),
                }
            )

    for item in sections.get(
        "therapy",
        [],
    ):
        if item.get(
            "progress_notes"
        ):
            highlights.append(
                {
                    "area": "THERAPY",
                    "text": (
                        item[
                            "progress_notes"
                        ]
                    ),
                }
            )

    for plan in sections.get(
        "planned_interventions",
        [],
    ):
        for followup in plan.get(
            "followups",
            [],
        ):
            if followup.get(
                "progress"
            ):
                highlights.append(
                    {
                        "area": (
                            "INTERVENTIONS"
                        ),
                        "text": (
                            followup[
                                "progress"
                            ]
                        ),
                    }
                )

    if highlights:
        summary["highlights"] = (
            highlights[:10]
        )

    return summary


def build_report_snapshot(
    *,
    student,
    report_type,
    generated_by,
    generated_role,
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

    if (
        report_type
        == StudentReport.ReportType.GENERAL
    ):
        base["sections"] = {
            "general": _student_value(
                student
            ),
        }

        return base

    if (
        report_type
        == StudentReport.ReportType.ACADEMIC
    ):
        items = _academic_items(
            student,
            date_from,
            date_to,
            generated_by,
            generated_role,
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
            generated_by,
            generated_role,
        )

        base["sections"] = {
            "psychological": items,
        }
        base["summary"] = {
            "total_records": len(items),
        }

        return base

    if (
        report_type
        == StudentReport.ReportType.THERAPY
    ):
        items = _therapy_items(
            student,
            date_from,
            date_to,
            generated_by,
            generated_role,
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
        performed = (
            _performed_interventions(
                student,
                date_from,
                date_to,
                generated_by,
                generated_role,
            )
        )

        planned = (
            _planned_interventions(
                student,
                date_from,
                date_to,
                generated_by,
                generated_role,
            )
        )

        base["sections"] = {
            "performed_interventions": (
                performed
            ),
            "planned_interventions": (
                planned
            ),
        }

        base["summary"] = {
            "performed_count": len(
                performed
            ),
            "planned_count": len(
                planned
            ),
        }

        return base

    if (
        report_type
        == StudentReport.ReportType.INTEGRAL
    ):
        sections = _build_integral_sections(
            student=student,
            generated_by=generated_by,
            generated_role=generated_role,
            date_from=date_from,
            date_to=date_to,
        )

        base["sections"] = sections

        summary = _build_integral_summary(
            sections=sections,
            generated_role=generated_role,
        )

        if summary:
            base["summary"] = summary

        return base

    raise ValueError(
        "Tipo de reporte no soportado."
    )
