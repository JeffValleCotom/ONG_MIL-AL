from rest_framework import exceptions

from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)

from .models import StudentReport


REPORT_TYPES_BY_CONTEXT = {
    "DOCENTE": {
        StudentReport.ReportType.ACADEMIC,
        StudentReport.ReportType.INTEGRAL,
    },
    "PSICOLOGO": {
        StudentReport.ReportType.PSYCHOLOGICAL,
        StudentReport.ReportType.INTERVENTIONS,
        StudentReport.ReportType.INTEGRAL,
    },
    "TERAPEUTA": {
        StudentReport.ReportType.THERAPY,
        StudentReport.ReportType.INTERVENTIONS,
        StudentReport.ReportType.INTEGRAL,
    },
    "RESPONSABLE_INSTITUCIONAL": {
        StudentReport.ReportType.GENERAL,
    },
}


def require_report_context(user, context):
    allowed_types = REPORT_TYPES_BY_CONTEXT.get(
        context,
    )

    if not allowed_types:
        raise exceptions.PermissionDenied(
            "El contexto indicado no permite consultar reportes."
        )

    has_permission = user.groups.filter(
        name=context,
        permissions__content_type__app_label="users",
        permissions__content_type__model="user",
        permissions__codename="view_reports",
    ).exists()

    if not has_permission:
        raise exceptions.PermissionDenied(
            "No tiene permisos para consultar reportes "
            "en este contexto."
        )

    return allowed_types


def require_report_type(
    user,
    context,
    report_type,
):
    allowed_types = require_report_context(
        user,
        context,
    )

    if report_type not in allowed_types:
        raise exceptions.PermissionDenied(
            "El tipo de reporte solicitado no está "
            "autorizado para este contexto."
        )


def get_report_student(
    user,
    context,
    student_id,
):
    require_report_context(
        user,
        context,
    )

    queryset = Student.objects.all()

    if context == "RESPONSABLE_INSTITUCIONAL":
        return queryset.filter(
            pk=student_id,
        ).first()

    if context in {
        "DOCENTE",
        "PSICOLOGO",
        "TERAPEUTA",
    }:
        return queryset.filter(
            pk=student_id,
            professional_assignments__professional=user,
            professional_assignments__professional_role=context,
            professional_assignments__is_active=True,
        ).distinct().first()

    return None


def get_accessible_report_queryset(
    user,
    context,
):
    allowed_types = require_report_context(
        user,
        context,
    )

    queryset = (
        StudentReport.objects
        .select_related(
            "student",
            "generated_by",
        )
        .filter(
            generated_by=user,
            generated_role=context,
            report_type__in=allowed_types,
        )
    )

    if context == "RESPONSABLE_INSTITUCIONAL":
        return queryset

    return queryset.filter(
        student__professional_assignments__professional=user,
        student__professional_assignments__professional_role=context,
        student__professional_assignments__is_active=True,
    ).distinct()
