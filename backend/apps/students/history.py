from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.therapy.models import TherapyFollowUp


EVALUATION_AREA_BY_ROLE = {
    "DOCENTE": "ACADEMICA",
    "PSICOLOGO": "PSICOLOGICA",
    "TERAPEUTA": "TERAPEUTICA",
}


def _user_summary(user):
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


def _history_entry(
    *,
    record,
    record_type,
    area,
    record_date,
    title,
    details,
):
    return (
        (
            record_date,
            record.created_at,
            record_type,
            record.id,
        ),
        {
            "record_id": record.id,
            "student_id": record.student_id,
            "record_type": record_type,
            "area": area,
            "date": record_date,
            "title": title,
            "details": details,
            "created_by": _user_summary(
                record.created_by
            ),
            "updated_by": _user_summary(
                record.updated_by
            ),
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        },
    )


def build_student_history(
    *,
    student,
    include_academic=False,
    include_psychological=False,
    include_therapy=False,
    evaluation_role=None,
):
    records = []

    if include_academic:
        followups = (
            AcademicFollowUp.objects
            .filter(student=student)
            .select_related(
                "created_by",
                "updated_by",
            )
        )

        for followup in followups:
            records.append(
                _history_entry(
                    record=followup,
                    record_type="ACADEMIC_FOLLOWUP",
                    area="ACADEMICA",
                    record_date=followup.followup_date,
                    title=followup.subject,
                    details={
                        "academic_period": (
                            followup.academic_period
                        ),
                        "subject": followup.subject,
                        "observations": (
                            followup.observations
                        ),
                        "strengths": followup.strengths,
                        "areas_for_improvement": (
                            followup.areas_for_improvement
                        ),
                        "recommendations": (
                            followup.recommendations
                        ),
                    },
                )
            )

    if include_psychological:
        followups = (
            PsychologicalFollowUp.objects
            .filter(student=student)
            .select_related(
                "created_by",
                "updated_by",
            )
        )

        for followup in followups:
            records.append(
                _history_entry(
                    record=followup,
                    record_type=(
                        "PSYCHOLOGICAL_FOLLOWUP"
                    ),
                    area="PSICOLOGICA",
                    record_date=followup.followup_date,
                    title=followup.reason,
                    details={
                        "reason": followup.reason,
                        "observations": (
                            followup.observations
                        ),
                        "emotional_behavioral_notes": (
                            followup
                            .emotional_behavioral_notes
                        ),
                        "recommendations": (
                            followup.recommendations
                        ),
                    },
                )
            )

    if include_therapy:
        followups = (
            TherapyFollowUp.objects
            .filter(student=student)
            .select_related(
                "created_by",
                "updated_by",
            )
        )

        for followup in followups:
            records.append(
                _history_entry(
                    record=followup,
                    record_type="THERAPY_FOLLOWUP",
                    area="TERAPEUTICA",
                    record_date=followup.followup_date,
                    title=followup.therapy_area,
                    details={
                        "therapy_area": (
                            followup.therapy_area
                        ),
                        "objectives": (
                            followup.objectives
                        ),
                        "activities": (
                            followup.activities
                        ),
                        "progress_notes": (
                            followup.progress_notes
                        ),
                        "recommendations": (
                            followup.recommendations
                        ),
                    },
                )
            )

    if evaluation_role:
        evaluations = (
            Evaluation.objects
            .filter(
                student=student,
                professional_role=evaluation_role,
            )
            .select_related(
                "created_by",
                "updated_by",
            )
        )

        evaluation_area = (
            EVALUATION_AREA_BY_ROLE[
                evaluation_role
            ]
        )

        for evaluation in evaluations:
            records.append(
                _history_entry(
                    record=evaluation,
                    record_type="EVALUATION",
                    area=evaluation_area,
                    record_date=(
                        evaluation.evaluation_date
                    ),
                    title=evaluation.evaluation_type,
                    details={
                        "evaluation_type": (
                            evaluation.evaluation_type
                        ),
                        "results": evaluation.results,
                        "observations": (
                            evaluation.observations
                        ),
                    },
                )
            )

    records.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        payload
        for _, payload in records
    ]
