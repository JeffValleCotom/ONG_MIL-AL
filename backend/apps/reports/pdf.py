from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


REPORT_TYPE_LABELS = {
    "GENERAL": "General",
    "ACADEMIC": "Académico",
    "PSYCHOLOGICAL": "Psicológico",
    "THERAPY": "Terapéutico",
    "INTERVENTIONS": "Intervenciones",
    "INTEGRAL": "Integral",
}


SECTION_LABELS = {
    "general": "Información general",
    "academic": "Seguimiento académico",
    "psychological": "Seguimiento psicológico",
    "therapy": "Seguimiento terapéutico",
    "evaluations": "Evaluaciones",
    "performed_interventions": (
        "Intervenciones realizadas"
    ),
    "planned_interventions": (
        "Intervenciones planificadas"
    ),
}


FIELD_LABELS = {
    "institutional_code": "Código institucional",
    "first_name": "Nombres",
    "last_name": "Apellidos",
    "date_of_birth": "Fecha de nacimiento",
    "admission_date": "Fecha de ingreso",
    "is_active": "Estado del estudiante",
    "date": "Fecha",
    "academic_period": "Período académico",
    "subject": "Asignatura",
    "observations": "Observaciones",
    "strengths": "Fortalezas",
    "areas_for_improvement": "Áreas de mejora",
    "recommendations": "Recomendaciones",
    "reason": "Motivo",
    "emotional_behavioral_notes": (
        "Notas emocionales y conductuales"
    ),
    "therapy_area": "Área terapéutica",
    "objectives": "Objetivos",
    "activities": "Actividades",
    "progress_notes": "Avances",
    "evaluation_type": "Tipo de evaluación",
    "results": "Resultados",
    "professional_role": "Rol profesional",
    "status": "Estado",
    "responsible_role": "Rol responsable",
    "estimated_start_date": "Inicio estimado",
    "estimated_end_date": "Fin estimado",
    "progress": "Avances",
    "responsible": "Responsable",
    "followups": "Historial de seguimientos",
}


SUMMARY_LABELS = {
    "total_records": "Total de registros",
    "performed_count": "Intervenciones realizadas",
    "planned_count": "Intervenciones planificadas",
    "academic_count": "Registros académicos",
    "psychological_count": "Registros psicológicos",
    "therapy_count": "Registros terapéuticos",
    "evaluation_count": "Evaluaciones",
    "performed_intervention_count": (
        "Intervenciones realizadas"
    ),
    "planned_intervention_count": (
        "Intervenciones planificadas"
    ),
    "highlights": "Principales avances",
}


def _safe(value):
    if value in (None, ""):
        return "—"

    if isinstance(value, bool):
        return "Sí" if value else "No"

    return escape(str(value))


def _person(value):
    if not isinstance(value, dict):
        return _safe(value)

    full_name = " ".join(
        part
        for part in [
            value.get("first_name"),
            value.get("last_name"),
        ]
        if part
    )

    return _safe(
        full_name
        or value.get("username")
        or "—"
    )


def _append_mapping(
    story,
    data,
    styles,
):
    for key, value in data.items():
        if key == "id":
            continue

        label = FIELD_LABELS.get(
            key,
            key.replace("_", " ").capitalize(),
        )

        if key == "responsible":
            story.append(
                Paragraph(
                    (
                        f"<b>{escape(label)}:</b> "
                        f"{_person(value)}"
                    ),
                    styles["BodyText"],
                )
            )
            continue

        if isinstance(value, list):
            story.append(
                Paragraph(
                    f"<b>{escape(label)}</b>",
                    styles["BodyText"],
                )
            )

            if not value:
                story.append(
                    Paragraph(
                        "Sin registros.",
                        styles["BodyText"],
                    )
                )

            for index, item in enumerate(
                value,
                start=1,
            ):
                story.append(
                    Spacer(1, 2 * mm)
                )

                story.append(
                    Paragraph(
                        f"{escape(label)} {index}",
                        styles["ReportSubheading"],
                    )
                )

                if isinstance(item, dict):
                    _append_mapping(
                        story,
                        item,
                        styles,
                    )
                else:
                    story.append(
                        Paragraph(
                            _safe(item),
                            styles["BodyText"],
                        )
                    )

            continue

        if isinstance(value, dict):
            story.append(
                Paragraph(
                    f"<b>{escape(label)}</b>",
                    styles["BodyText"],
                )
            )

            _append_mapping(
                story,
                value,
                styles,
            )
            continue

        story.append(
            Paragraph(
                (
                    f"<b>{escape(label)}:</b> "
                    f"{_safe(value)}"
                ),
                styles["BodyText"],
            )
        )


def build_report_pdf(report):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=(
            "Reporte MIL-AL - "
            f"{report.get_report_type_display()}"
        ),
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportSubheading",
            parent=styles["Heading4"],
            spaceBefore=6,
            spaceAfter=4,
        )
    )

    snapshot = report.content_snapshot or {}

    story = [
        Paragraph(
            "ONG MIL-AL",
            styles["Title"],
        ),
        Paragraph(
            (
                "Reporte "
                + escape(
                    REPORT_TYPE_LABELS.get(
                        report.report_type,
                        report.report_type,
                    )
                )
            ),
            styles["Heading2"],
        ),
        Spacer(1, 4 * mm),
        Paragraph(
            (
                "<b>Estudiante:</b> "
                f"{_safe(report.student.first_name)} "
                f"{_safe(report.student.last_name)}"
            ),
            styles["BodyText"],
        ),
        Paragraph(
            (
                "<b>Código institucional:</b> "
                f"{_safe(report.student.institutional_code)}"
            ),
            styles["BodyText"],
        ),
        Paragraph(
            (
                "<b>Contexto:</b> "
                f"{_safe(report.generated_role)}"
            ),
            styles["BodyText"],
        ),
        Paragraph(
            (
                "<b>Fecha de generación:</b> "
                f"{_safe(report.generated_at)}"
            ),
            styles["BodyText"],
        ),
        Paragraph(
            (
                "<b>Período:</b> "
                f"{_safe(report.date_from)} — "
                f"{_safe(report.date_to)}"
            ),
            styles["BodyText"],
        ),
        Spacer(1, 6 * mm),
    ]

    summary = snapshot.get("summary")

    if isinstance(summary, dict):
        story.append(
            Paragraph(
                "Resumen",
                styles["Heading2"],
            )
        )

        for key, value in summary.items():
            label = SUMMARY_LABELS.get(
                key,
                key.replace("_", " ").capitalize(),
            )

            if key == "highlights":
                if value:
                    story.append(
                        Paragraph(
                            "<b>Principales avances</b>",
                            styles["BodyText"],
                        )
                    )

                    for highlight in value:
                        story.append(
                            Paragraph(
                                (
                                    "• "
                                    f"<b>{_safe(highlight.get('area'))}:</b> "
                                    f"{_safe(highlight.get('text'))}"
                                ),
                                styles["BodyText"],
                            )
                        )

                continue

            story.append(
                Paragraph(
                    (
                        f"<b>{escape(label)}:</b> "
                        f"{_safe(value)}"
                    ),
                    styles["BodyText"],
                )
            )

        story.append(
            Spacer(1, 5 * mm)
        )

    sections = snapshot.get(
        "sections",
        {},
    )

    for section_name, content in sections.items():
        story.append(
            Paragraph(
                escape(
                    SECTION_LABELS.get(
                        section_name,
                        section_name,
                    )
                ),
                styles["Heading2"],
            )
        )

        if isinstance(content, list):
            if not content:
                story.append(
                    Paragraph(
                        "No hay registros en el período seleccionado.",
                        styles["BodyText"],
                    )
                )

            for index, item in enumerate(
                content,
                start=1,
            ):
                story.append(
                    Paragraph(
                        f"Registro {index}",
                        styles["ReportSubheading"],
                    )
                )

                _append_mapping(
                    story,
                    item,
                    styles,
                )

                story.append(
                    Spacer(1, 4 * mm)
                )

        elif isinstance(content, dict):
            _append_mapping(
                story,
                content,
                styles,
            )

        story.append(
            Spacer(1, 5 * mm)
        )

    document.build(story)

    return buffer.getvalue()
