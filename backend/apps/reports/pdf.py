
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPORT_TYPE_LABELS = {
    "GENERAL": "General",
    "ACADEMIC": "Académico",
    "PSYCHOLOGICAL": "Psicológico",
    "THERAPY": "Terapéutico",
    "INTERVENTIONS": "Intervenciones",
    "INTEGRAL": "Integral",
}

REPORT_TITLE_LABELS = {
    "GENERAL": "Informe general de seguimiento",
    "ACADEMIC": "Informe académico de seguimiento",
    "PSYCHOLOGICAL": "Informe psicológico de seguimiento",
    "THERAPY": "Informe terapéutico de seguimiento",
    "INTERVENTIONS": "Informe de intervenciones",
    "INTEGRAL": "Informe integral de seguimiento",
}

SECTION_LABELS = {
    "general": "Información general del estudiante",
    "academic": "Seguimiento académico",
    "psychological": "Seguimiento psicológico",
    "therapy": "Seguimiento terapéutico",
    "evaluations": "Resultados de evaluaciones",
    "performed_interventions": "Intervenciones realizadas",
    "planned_interventions": "Plan de intervención",
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
    "emotional_behavioral_notes": "Notas emocionales y conductuales",
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
    "performed_intervention_count": "Intervenciones realizadas",
    "planned_intervention_count": "Intervenciones planificadas",
}

ROLE_LABELS = {
    "DOCENTE": "Docente",
    "PSICOLOGO": "Psicólogo",
    "TERAPEUTA": "Terapeuta",
    "RESPONSABLE_INSTITUCIONAL": "Responsable institucional",
}

STATUS_LABELS = {
    "PLANNED": "Planificada",
    "IN_PROGRESS": "En progreso",
    "COMPLETED": "Completada",
    "CANCELLED": "Cancelada",
}

DATE_FIELDS = {
    "date",
    "date_of_birth",
    "admission_date",
    "estimated_start_date",
    "estimated_end_date",
}


# Paleta institucional: navy + verde de la aplicación.
NAVY = HexColor("#17243A")
NAVY_2 = HexColor("#21324E")
GREEN = HexColor("#3A9624")
GREEN_DARK = HexColor("#2F7D1E")
GREEN_LIGHT = HexColor("#EAF5E6")
GREEN_PALE = HexColor("#F4FAF1")

TEXT = HexColor("#27364A")
MUTED = HexColor("#667085")
BORDER = HexColor("#D7E0E9")
SURFACE = HexColor("#F7F9FC")
BLUE_LIGHT = HexColor("#EAF2FF")
YELLOW_LIGHT = HexColor("#FFF5D9")
GRAY_LIGHT = HexColor("#F1F3F5")
WHITE = colors.white

STATUS_PALETTE = {
    "PLANNED": (
        YELLOW_LIGHT,
        HexColor("#8A6500"),
    ),
    "IN_PROGRESS": (
        BLUE_LIGHT,
        HexColor("#245BA7"),
    ),
    "COMPLETED": (
        GREEN_LIGHT,
        GREEN_DARK,
    ),
    "CANCELLED": (
        GRAY_LIGHT,
        HexColor("#6B7280"),
    ),
}


def _safe(value):
    if value in (None, ""):
        return "—"

    if isinstance(value, bool):
        return "Sí" if value else "No"

    return escape(str(value))


def _format_date(value):
    if value in (None, ""):
        return "—"

    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")

    try:
        return datetime.strptime(
            str(value)[:10],
            "%Y-%m-%d",
        ).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return _safe(value)


def _format_datetime(value):
    if isinstance(value, datetime):
        current = (
            timezone.localtime(value)
            if timezone.is_aware(value)
            else value
        )
        return current.strftime(
            "%d/%m/%Y · %H:%M"
        )

    return _safe(value)


def _format_role(value):
    if value in (None, ""):
        return "—"

    raw = str(value).upper()

    return escape(
        ROLE_LABELS.get(
            raw,
            raw.replace("_", " ").title(),
        )
    )


def _format_status(value):
    if value in (None, ""):
        return "—"

    raw = str(value).upper()

    return escape(
        STATUS_LABELS.get(
            raw,
            raw.replace("_", " ").title(),
        )
    )


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
    ).strip()

    return _safe(
        full_name
        or value.get("username")
        or "—"
    )


def _user_name(user):
    if not user:
        return "—"

    get_full_name = getattr(
        user,
        "get_full_name",
        None,
    )

    if callable(get_full_name):
        full_name = get_full_name()

        if full_name:
            return escape(full_name)

    return _safe(
        getattr(user, "username", None)
        or str(user)
    )


def _student_name(report):
    return " ".join(
        part
        for part in [
            report.student.first_name,
            report.student.last_name,
        ]
        if part
    ).strip() or "Estudiante"


def _format_value(key, value):
    if key == "responsible":
        return _person(value)

    if key in DATE_FIELDS:
        return _format_date(value)

    if key in {
        "professional_role",
        "responsible_role",
    }:
        return _format_role(value)

    if key == "status":
        return _format_status(value)

    if (
        key == "is_active"
        and isinstance(value, bool)
    ):
        return (
            "Activo"
            if value
            else "Inactivo"
        )

    return _safe(value)


def _styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            "CoverKicker",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=GREEN_DARK,
            spaceAfter=2 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverBrand",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=27,
            alignment=TA_CENTER,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverOrg",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=MUTED,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            alignment=TA_CENTER,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverStudent",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "CoverMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            alignment=TA_LEFT,
            textColor=TEXT,
        )
    )

    styles.add(
        ParagraphStyle(
            "HeaderBrand",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=10,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "HeaderMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=6.5,
            leading=8.5,
            alignment=TA_RIGHT,
            textColor=MUTED,
        )
    )

    styles.add(
        ParagraphStyle(
            "IndexTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=20,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "IndexNumber",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=WHITE,
        )
    )

    styles.add(
        ParagraphStyle(
            "IndexItem",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=TEXT,
        )
    )

    styles.add(
        ParagraphStyle(
            "SectionNumber",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            textColor=WHITE,
        )
    )

    styles.add(
        ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=WHITE,
            keepWithNext=True,
        )
    )

    styles.add(
        ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=TEXT,
        )
    )

    styles.add(
        ParagraphStyle(
            "BodySmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.5,
            textColor=TEXT,
        )
    )

    styles.add(
        ParagraphStyle(
            "FieldLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "FieldLabelMuted",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.5,
            textColor=MUTED,
        )
    )

    styles.add(
        ParagraphStyle(
            "CardTitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "SubCardTitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.2,
            leading=10,
            textColor=GREEN_DARK,
        )
    )

    styles.add(
        ParagraphStyle(
            "MetricValue",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=18,
            alignment=TA_CENTER,
            textColor=GREEN_DARK,
        )
    )

    styles.add(
        ParagraphStyle(
            "MetricLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.5,
            alignment=TA_CENTER,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "Status",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.5,
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            "Empty",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=7.6,
            leading=10,
            textColor=MUTED,
        )
    )

    styles.add(
        ParagraphStyle(
            "ClosingTitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=NAVY,
        )
    )

    styles.add(
        ParagraphStyle(
            "FooterNote",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=6.3,
            leading=8.3,
            textColor=MUTED,
        )
    )

    return styles


def _logo_path():
    """
    Coloca el logo REAL de la ONG en:
    backend/apps/reports/assets/ong-milal-logo.png

    Si no existe, el PDF usa solo el wordmark MIL-AL ONG.
    """
    return (
        Path(__file__).resolve().parent
        / "assets"
        / "ong-milal-logo.png"
    )


def _logo_flowable(
    width=26 * mm,
    height=15 * mm,
):
    path = _logo_path()

    if not path.exists():
        return None

    image = Image(
        str(path),
        width=width,
        height=height,
    )

    image.hAlign = "CENTER"

    return image


def _brand_wordmark(
    styles,
    align=TA_LEFT,
):
    style = ParagraphStyle(
        "DynamicBrand",
        parent=styles["HeaderBrand"],
        alignment=align,
    )

    return Paragraph(
        "MIL-AL<br/><font size='6'>ONG</font>",
        style,
    )


def _period(report):
    return (
        f"{_format_date(report.date_from)}"
        f" - {_format_date(report.date_to)}"
    )


def _cover_story(
    report,
    styles,
):
    title = REPORT_TITLE_LABELS.get(
        report.report_type,
        "Informe institucional",
    )

    logo = _logo_flowable(
        36 * mm,
        22 * mm,
    )

    story = [
        Spacer(
            1,
            35 * mm,
        )
    ]

    if logo:
        story.extend(
            [
                logo,
                Spacer(
                    1,
                    3 * mm,
                ),
            ]
        )
    else:
        story.extend(
            [
                Paragraph(
                    "MIL-AL",
                    styles["CoverBrand"],
                ),
                Paragraph(
                    "ONG",
                    styles["CoverOrg"],
                ),
            ]
        )

    story.extend(
        [
            Paragraph(
                "ORGANIZACIÓN NO GUBERNAMENTAL",
                styles["CoverKicker"],
            ),
            Paragraph(
                "Plataforma de Seguimiento Estudiantil",
                styles["CoverOrg"],
            ),
            Spacer(
                1,
                13 * mm,
            ),
            HRFlowable(
                width=28 * mm,
                thickness=2.4,
                color=GREEN,
                hAlign="CENTER",
                spaceAfter=7 * mm,
            ),
            Paragraph(
                escape(title),
                styles["CoverTitle"],
            ),
            Spacer(
                1,
                14 * mm,
            ),
        ]
    )

    meta = Table(
        [
            [
                Paragraph(
                    "ESTUDIANTE",
                    styles["FieldLabelMuted"],
                ),
                Paragraph(
                    _safe(
                        _student_name(report)
                    ),
                    styles["CoverStudent"],
                ),
            ],
            [
                Paragraph(
                    "CÓDIGO",
                    styles["FieldLabelMuted"],
                ),
                Paragraph(
                    _safe(
                        report.student.institutional_code
                    ),
                    styles["CoverMeta"],
                ),
            ],
            [
                Paragraph(
                    "PERÍODO",
                    styles["FieldLabelMuted"],
                ),
                Paragraph(
                    _period(report),
                    styles["CoverMeta"],
                ),
            ],
            [
                Paragraph(
                    "FECHA DE EMISIÓN",
                    styles["FieldLabelMuted"],
                ),
                Paragraph(
                    _format_datetime(
                        report.generated_at
                    ),
                    styles["CoverMeta"],
                ),
            ],
        ],
        colWidths=[
            44 * mm,
            82 * mm,
        ],
        hAlign="CENTER",
    )

    meta.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.45,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.8 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.8 * mm,
                ),
            ]
        )
    )

    story.extend(
        [
            meta,
            PageBreak(),
        ]
    )

    return story


def _inner_header(
    report,
    styles,
):
    logo = _logo_flowable(
        21 * mm,
        12 * mm,
    )

    left = (
        logo
        if logo
        else _brand_wordmark(
            styles
        )
    )

    right = Paragraph(
        (
            f"<b>{escape(REPORT_TITLE_LABELS.get(report.report_type, 'Informe institucional'))}</b>"
            f"<br/>Período: {_period(report)}"
        ),
        styles["HeaderMeta"],
    )

    table = Table(
        [[
            left,
            right,
        ]],
        colWidths=[
            52 * mm,
            122 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    return [
        table,
        Spacer(
            1,
            2 * mm,
        ),
        HRFlowable(
            width="100%",
            thickness=1.1,
            color=GREEN,
            spaceAfter=4 * mm,
        ),
    ]


def _section_bar(
    number,
    title,
    styles,
):
    table = Table(
        [[
            Paragraph(
                str(number),
                styles["SectionNumber"],
            ),
            Paragraph(
                escape(title),
                styles["SectionTitle"],
            ),
        ]],
        colWidths=[
            12 * mm,
            162 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    GREEN,
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    NAVY,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.6 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.6 * mm,
                ),
            ]
        )
    )

    return table


def _section_names(
    snapshot,
):
    result = []

    if isinstance(
        snapshot.get("summary"),
        dict,
    ):
        result.append(
            "Resumen del período"
        )

    sections = snapshot.get(
        "sections",
        {},
    )

    if isinstance(
        sections,
        dict,
    ):
        for key in sections:
            result.append(
                SECTION_LABELS.get(
                    key,
                    key.replace(
                        "_",
                        " ",
                    ).capitalize(),
                )
            )

    result.append(
        "Información del documento"
    )

    return result


def _index_story(
    report,
    snapshot,
    styles,
):
    story = []

    story.extend(
        [
            Spacer(
                1,
                5 * mm,
            ),
            Paragraph(
                "Índice de contenido",
                styles["IndexTitle"],
            ),
            Spacer(
                1,
                5 * mm,
            ),
        ]
    )

    names = [
        "Ficha del reporte",
        *_section_names(snapshot),
    ]

    rows = []

    for index, label in enumerate(
        names,
        start=1,
    ):
        number = Table(
            [[
                Paragraph(
                    str(index),
                    styles["IndexNumber"],
                )
            ]],
            colWidths=[8 * mm],
            rowHeights=[8 * mm],
        )

        number.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        GREEN,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                ]
            )
        )

        rows.append(
            [
                number,
                Paragraph(
                    escape(label),
                    styles["IndexItem"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[
            13 * mm,
            161 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5 * mm,
                ),
            ]
        )
    )

    story.extend(
        [
            table,
            PageBreak(),
        ]
    )

    return story


def _report_facts(
    report,
    styles,
):
    rows = [
        [
            "Estudiante",
            _student_name(report),
        ],
        [
            "Código",
            report.student.institutional_code,
        ],
        [
            "Contexto",
            _format_role(
                report.generated_role
            ),
        ],
        [
            "Período",
            _period(report),
        ],
        [
            "Generado por",
            _user_name(
                getattr(
                    report,
                    "generated_by",
                    None,
                )
            ),
        ],
        [
            "Fecha de emisión",
            _format_datetime(
                report.generated_at
            ),
        ],
    ]

    table_data = []

    for label, value in rows:
        table_data.append(
            [
                Paragraph(
                    escape(label),
                    styles["FieldLabel"],
                ),
                Paragraph(
                    _safe(value),
                    styles["Body"],
                ),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            48 * mm,
            126 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    SURFACE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    BORDER,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.35,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.4 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.4 * mm,
                ),
            ]
        )
    )

    return table


def _metric_card(
    value,
    label,
    styles,
):
    table = Table(
        [
            [
                Paragraph(
                    _safe(value),
                    styles["MetricValue"],
                )
            ],
            [
                Paragraph(
                    escape(label),
                    styles["MetricLabel"],
                )
            ],
        ],
        colWidths=[54 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GREEN_PALE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    BORDER,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    0.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, 1),
                    0.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, 1),
                    3 * mm,
                ),
            ]
        )
    )

    return table


def _summary_cards(
    summary,
    styles,
):
    cards = []
    seen = set()

    for key, value in summary.items():
        if key == "highlights":
            continue

        label = SUMMARY_LABELS.get(
            key,
            key.replace("_", " ").capitalize(),
        )

        fingerprint = (
            label,
            str(value),
        )

        if fingerprint in seen:
            continue

        seen.add(fingerprint)

        cards.append(
            _metric_card(
                value,
                label,
                styles,
            )
        )

    if not cards:
        return None

    rows = []

    for start in range(
        0,
        len(cards),
        3,
    ):
        row = cards[start:start + 3]
        row.extend(
            [""] * (3 - len(row))
        )
        rows.append(row)

    table = Table(
        rows,
        colWidths=[
            58 * mm,
            58 * mm,
            58 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1.5 * mm,
                ),
            ]
        )
    )

    return table


def _status_cell(
    status,
    styles,
):
    raw = (
        str(status).upper()
        if status
        else ""
    )

    bg, fg = STATUS_PALETTE.get(
        raw,
        (
            SURFACE,
            MUTED,
        ),
    )

    style = ParagraphStyle(
        "StatusDynamic",
        parent=styles["Status"],
        textColor=fg,
    )

    table = Table(
        [[
            Paragraph(
                _format_status(status),
                style,
            )
        ]],
        colWidths=[30 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    bg,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.55,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1.4 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1.4 * mm,
                ),
            ]
        )
    )

    return table


def _field_rows(
    data,
    styles,
    *,
    exclude=None,
):
    exclude = set(
        exclude
        or []
    )

    rows = []

    for key, value in data.items():
        if (
            key == "id"
            or key in exclude
            or isinstance(
                value,
                (list, dict),
            )
        ):
            continue

        label = FIELD_LABELS.get(
            key,
            key.replace(
                "_",
                " ",
            ).capitalize(),
        )

        rows.append(
            [
                Paragraph(
                    escape(label),
                    styles["FieldLabel"],
                ),
                Paragraph(
                    _format_value(
                        key,
                        value,
                    ),
                    styles["Body"],
                ),
            ]
        )

    return rows


def _responsible_row(
    responsible,
    styles,
):
    if not responsible:
        return None

    return [
        Paragraph(
            "Responsable",
            styles["FieldLabel"],
        ),
        Paragraph(
            _person(responsible),
            styles["Body"],
        ),
    ]


def _record_card(
    data,
    styles,
    title,
):
    if not isinstance(
        data,
        dict,
    ):
        return [
            Paragraph(
                _safe(data),
                styles["Body"],
            )
        ]

    status = data.get("status")
    responsible = data.get(
        "responsible"
    )

    rows = _field_rows(
        data,
        styles,
        exclude={
            "status",
            "responsible",
            "followups",
        },
    )

    responsible_line = _responsible_row(
        responsible,
        styles,
    )

    if responsible_line:
        rows.append(
            responsible_line
        )

    header_right = (
        _status_cell(
            status,
            styles,
        )
        if status
        else ""
    )

    data_table = Table(
        rows,
        colWidths=[
            48 * mm,
            126 * mm,
        ],
    )

    data_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.white,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.3,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.1 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.1 * mm,
                ),
            ]
        )
    )

    header = Table(
        [[
            Paragraph(
                escape(title),
                styles["CardTitle"],
            ),
            header_right,
        ]],
        colWidths=[
            139 * mm,
            35 * mm,
        ],
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GREEN_PALE,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
            ]
        )
    )

    card = Table(
        [
            [header],
            [data_table],
        ],
        colWidths=[174 * mm],
    )

    card.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.75,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    return [
        KeepTogether([card]),
    ]


def _followup_cards(
    followups,
    styles,
):
    story = []

    if not followups:
        story.append(
            Paragraph(
                "Sin registros de seguimiento.",
                styles["Empty"],
            )
        )
        return story

    story.append(
        Paragraph(
            "HISTORIAL DE SEGUIMIENTOS",
            styles["SubCardTitle"],
        )
    )

    story.append(
        Spacer(
            1,
            1.5 * mm,
        )
    )

    for index, followup in enumerate(
        followups,
        start=1,
    ):
        story.extend(
            _record_card(
                followup,
                styles,
                f"Seguimiento {index:02d}",
            )
        )

        story.append(
            Spacer(
                1,
                2.5 * mm,
            )
        )

    return story


def _generic_section(
    content,
    styles,
):
    story = []

    if isinstance(
        content,
        list,
    ):
        if not content:
            return [
                _empty_box(
                    styles
                )
            ]

        for index, item in enumerate(
            content,
            start=1,
        ):
            story.extend(
                _record_card(
                    item,
                    styles,
                    f"Registro {index:02d}",
                )
            )

            story.append(
                Spacer(
                    1,
                    3 * mm,
                )
            )

        return story

    if isinstance(
        content,
        dict,
    ):
        if not content:
            return [
                _empty_box(
                    styles
                )
            ]

        return _record_card(
            content,
            styles,
            "Detalle",
        )

    return [
        Paragraph(
            _safe(content),
            styles["Body"],
        )
    ]


def _planned_section(
    content,
    styles,
):
    if not isinstance(
        content,
        list,
    ):
        return _generic_section(
            content,
            styles,
        )

    if not content:
        return [
            _empty_box(
                styles
            )
        ]

    story = []

    for index, plan in enumerate(
        content,
        start=1,
    ):
        story.extend(
            _record_card(
                plan,
                styles,
                f"Registro {index:02d}",
            )
        )

        followups = (
            plan.get("followups")
            if isinstance(
                plan,
                dict,
            )
            else None
        )

        if followups is not None:
            story.append(
                Spacer(
                    1,
                    2 * mm,
                )
            )

            story.extend(
                _followup_cards(
                    followups,
                    styles,
                )
            )

        story.append(
            Spacer(
                1,
                4 * mm,
            )
        )

    return story


def _highlights_box(
    highlights,
    styles,
):
    if not highlights:
        return None

    rows = []

    for highlight in highlights:
        if isinstance(
            highlight,
            dict,
        ):
            area = _safe(
                highlight.get("area")
            )
            text = _safe(
                highlight.get("text")
            )
        else:
            area = "Avance"
            text = _safe(highlight)

        rows.append(
            [
                Paragraph(
                    area,
                    styles["FieldLabel"],
                ),
                Paragraph(
                    text,
                    styles["Body"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[
            42 * mm,
            132 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GREEN_PALE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.3,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.3 * mm,
                ),
            ]
        )
    )

    return table


def _empty_box(
    styles,
):
    table = Table(
        [[
            Paragraph(
                "No hay registros en el período seleccionado.",
                styles["Empty"],
            )
        ]],
        colWidths=[174 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    SURFACE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
            ]
        )
    )

    return table


def _closing_box(
    report,
    styles,
):
    rows = [
        [
            "Tipo de reporte",
            REPORT_TYPE_LABELS.get(
                report.report_type,
                report.report_type,
            ),
        ],
        [
            "ID del reporte",
            getattr(
                report,
                "id",
                "—",
            ),
        ],
        [
            "Contexto",
            _format_role(
                report.generated_role
            ),
        ],
        [
            "Generado por",
            _user_name(
                getattr(
                    report,
                    "generated_by",
                    None,
                )
            ),
        ],
        [
            "Fecha y hora",
            _format_datetime(
                report.generated_at
            ),
        ],
    ]

    data = []

    for label, value in rows:
        data.append(
            [
                Paragraph(
                    escape(str(label)),
                    styles["FieldLabel"],
                ),
                Paragraph(
                    _safe(value),
                    styles["Body"],
                ),
            ]
        )

    table = Table(
        data,
        colWidths=[
            52 * mm,
            122 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    SURFACE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    BORDER,
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -2),
                    0.3,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3.5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.4 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.4 * mm,
                ),
            ]
        )
    )

    return table


def _draw_cover(
    canvas,
    document,
):
    canvas.saveState()

    width, height = A4

    # Bloque superior navy.
    canvas.setFillColor(NAVY)
    canvas.rect(
        0,
        height - 25 * mm,
        width,
        25 * mm,
        stroke=0,
        fill=1,
    )

    # Acento superior verde.
    canvas.setFillColor(GREEN)
    canvas.rect(
        0,
        height - 30 * mm,
        width * 0.36,
        5 * mm,
        stroke=0,
        fill=1,
    )

    # Cinta inferior.
    canvas.setFillColor(NAVY)
    canvas.rect(
        0,
        0,
        width,
        14 * mm,
        stroke=0,
        fill=1,
    )

    canvas.setFillColor(GREEN)
    canvas.rect(
        0,
        14 * mm,
        width,
        5 * mm,
        stroke=0,
        fill=1,
    )

    # Panel decorativo lateral.
    canvas.setFillColor(GREEN_PALE)
    canvas.roundRect(
        width - 30 * mm,
        36 * mm,
        22 * mm,
        120 * mm,
        6 * mm,
        stroke=0,
        fill=1,
    )

    canvas.restoreState()


def _draw_inner(
    canvas,
    document,
    report,
):
    canvas.saveState()

    width, height = A4
    logo_path = _logo_path()

    if logo_path.exists():
        try:
            image = ImageReader(
                str(logo_path)
            )
            canvas.drawImage(
                image,
                18 * mm,
                height - 16 * mm,
                width=19 * mm,
                height=11 * mm,
                preserveAspectRatio=True,
                mask="auto",
                anchor="sw",
            )
        except Exception:
            canvas.setFillColor(NAVY)
            canvas.setFont(
                "Helvetica-Bold",
                8.5,
            )
            canvas.drawString(
                18 * mm,
                height - 11.5 * mm,
                "MIL-AL",
            )
    else:
        canvas.setFillColor(NAVY)
        canvas.setFont(
            "Helvetica-Bold",
            8.5,
        )
        canvas.drawString(
            18 * mm,
            height - 11.5 * mm,
            "MIL-AL",
        )

        canvas.setFont(
            "Helvetica",
            5.5,
        )
        canvas.drawString(
            18 * mm,
            height - 14 * mm,
            "ONG",
        )

    title = REPORT_TITLE_LABELS.get(
        report.report_type,
        "Informe institucional",
    )

    canvas.setFillColor(NAVY)
    canvas.setFont(
        "Helvetica-Bold",
        6.5,
    )
    canvas.drawRightString(
        width - 18 * mm,
        height - 10.5 * mm,
        title,
    )

    canvas.setFillColor(MUTED)
    canvas.setFont(
        "Helvetica",
        5.8,
    )
    canvas.drawRightString(
        width - 18 * mm,
        height - 14 * mm,
        f"Período: {_period(report)}",
    )

    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1)
    canvas.line(
        18 * mm,
        height - 18 * mm,
        width - 18 * mm,
        height - 18 * mm,
    )

    canvas.setFillColor(GREEN)
    canvas.rect(
        0,
        0,
        width,
        4 * mm,
        stroke=0,
        fill=1,
    )

    canvas.setFillColor(NAVY)
    canvas.rect(
        0,
        4 * mm,
        width,
        5 * mm,
        stroke=0,
        fill=1,
    )

    canvas.setFillColor(WHITE)
    canvas.setFont(
        "Helvetica",
        6.2,
    )
    canvas.drawString(
        18 * mm,
        5.5 * mm,
        "ONG MIL-AL · Reporte institucional",
    )

    canvas.drawRightString(
        width - 18 * mm,
        5.5 * mm,
        f"Página {document.page}",
    )

    canvas.restoreState()


def build_report_pdf(report):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title=REPORT_TITLE_LABELS.get(
            report.report_type,
            "Informe institucional",
        ),
        author="ONG MIL-AL",
        subject="Seguimiento estudiantil",
    )

    styles = _styles()
    snapshot = (
        report.content_snapshot
        or {}
    )

    story = []

    story.extend(
        _cover_story(
            report,
            styles,
        )
    )

    if report.report_type == "INTEGRAL":
        story.extend(
            _index_story(
                report,
                snapshot,
                styles,
            )
        )

    section_number = 1

    story.extend(
        [
            _section_bar(
                section_number,
                "Ficha del reporte",
                styles,
            ),
            Spacer(
                1,
                3 * mm,
            ),
            _report_facts(
                report,
                styles,
            ),
            Spacer(
                1,
                5 * mm,
            ),
        ]
    )

    section_number += 1

    summary = snapshot.get(
        "summary"
    )

    if isinstance(
        summary,
        dict,
    ):
        story.extend(
            [
                _section_bar(
                    section_number,
                    "Resumen del período",
                    styles,
                ),
                Spacer(
                    1,
                    3 * mm,
                ),
            ]
        )

        cards = _summary_cards(
            summary,
            styles,
        )

        if cards:
            story.append(cards)

        highlights = (
            summary.get("highlights")
            or []
        )

        if highlights:
            story.extend(
                [
                    Spacer(
                        1,
                        3 * mm,
                    ),
                    Paragraph(
                        "Principales avances",
                        styles["SubCardTitle"],
                    ),
                    Spacer(
                        1,
                        1.5 * mm,
                    ),
                ]
            )

            box = _highlights_box(
                highlights,
                styles,
            )

            if box:
                story.append(box)

        story.append(
            Spacer(
                1,
                5 * mm,
            )
        )

        section_number += 1

    sections = snapshot.get(
        "sections",
        {},
    )

    if isinstance(
        sections,
        dict,
    ):
        for key, content in sections.items():
            title = SECTION_LABELS.get(
                key,
                key.replace(
                    "_",
                    " ",
                ).capitalize(),
            )

            story.extend(
                [
                    _section_bar(
                        section_number,
                        title,
                        styles,
                    ),
                    Spacer(
                        1,
                        3 * mm,
                    ),
                ]
            )

            if key == "planned_interventions":
                story.extend(
                    _planned_section(
                        content,
                        styles,
                    )
                )
            else:
                story.extend(
                    _generic_section(
                        content,
                        styles,
                    )
                )

            story.append(
                Spacer(
                    1,
                    4.5 * mm,
                )
            )

            section_number += 1

    story.extend(
        [
            _section_bar(
                section_number,
                "Información del documento",
                styles,
            ),
            Spacer(
                1,
                3 * mm,
            ),
            _closing_box(
                report,
                styles,
            ),
            Spacer(
                1,
                2.5 * mm,
            ),
            Paragraph(
                (
                    "Documento institucional de uso autorizado. "
                    "El contenido corresponde al snapshot generado "
                    "para el contexto profesional permitido."
                ),
                styles["FooterNote"],
            ),
        ]
    )

    document.build(
        story,
        onFirstPage=_draw_cover,
        onLaterPages=(
            lambda canvas, doc: _draw_inner(
                canvas,
                doc,
                report,
            )
        ),
    )

    return buffer.getvalue()
