from apps.reports.services import (
    build_student_data_sections,
)


SECTIONS_BY_CONTEXT = {
    "DOCENTE": (
        "academic",
        "evaluations",
    ),
    "PSICOLOGO": (
        "psychological",
        "evaluations",
        "performed_interventions",
        "planned_interventions",
    ),
    "TERAPEUTA": (
        "therapy",
        "evaluations",
        "performed_interventions",
        "planned_interventions",
    ),
}


REMOVED_CONTEXT_KEYS = {
    "id",
    "responsible",
}


def _date_value(value):
    if value is None:
        return None

    return value.isoformat()


def _sanitize_context(value):
    if isinstance(value, list):
        return [
            _sanitize_context(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _sanitize_context(item)
            for key, item in value.items()
            if key not in REMOVED_CONTEXT_KEYS
        }

    return value


def build_ai_context(
    *,
    student,
    context,
    date_from=None,
    date_to=None,
):
    try:
        sections = SECTIONS_BY_CONTEXT[
            context
        ]
    except KeyError as exc:
        raise ValueError(
            "Contexto profesional "
            "no soportado para IA."
        ) from exc

    raw_sections = (
        build_student_data_sections(
            student=student,
            sections=sections,
            date_from=date_from,
            date_to=date_to,
        )
    )

    return {
        "context": context,
        "period": {
            "date_from": _date_value(
                date_from
            ),
            "date_to": _date_value(
                date_to
            ),
        },
        "sections": _sanitize_context(
            raw_sections
        ),
    }


def build_report_ai_context(
    report,
):
    snapshot = (
        report.content_snapshot
        or {}
    )

    return {
        "source": "REPORT",
        "context": report.generated_role,
        "report_type": report.report_type,
        "period": {
            "date_from": _date_value(
                report.date_from
            ),
            "date_to": _date_value(
                report.date_to
            ),
        },
        "summary": _sanitize_context(
            snapshot.get(
                "summary",
                {},
            )
        ),
        "sections": _sanitize_context(
            snapshot.get(
                "sections",
                {},
            )
        ),
    }