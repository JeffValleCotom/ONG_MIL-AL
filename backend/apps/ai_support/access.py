from django.shortcuts import get_object_or_404
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from apps.students.models import Student
from .models import AIInsight
from apps.reports.access import (
    get_accessible_report_queryset,
)


AI_CONTEXTS = {
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
}


def require_ai_context(
    user,
    context,
):
    context = (
        context or ""
    ).strip().upper()

    if context not in AI_CONTEXTS:
        raise ValidationError(
            {
                "context": (
                    "Contexto profesional "
                    "no válido para IA."
                )
            }
        )

    if not user.groups.filter(
        name=context
    ).exists():
        raise PermissionDenied(
            "El usuario no pertenece "
            "al contexto solicitado."
        )

    if not user.has_perm(
        "users.use_ai_assistant"
    ):
        raise PermissionDenied(
            "El usuario no tiene permiso "
            "para utilizar el asistente "
            "de inteligencia artificial."
        )

    return context


def get_ai_student(
    user,
    context,
    student_id,
):
    context = require_ai_context(
        user,
        context,
    )

    queryset = (
        Student.objects
        .filter(
            professional_assignments__professional=(
                user
            ),
            professional_assignments__professional_role=(
                context
            ),
            professional_assignments__is_active=True,
        )
        .distinct()
    )

    return get_object_or_404(
        queryset,
        pk=student_id,
    )

def get_accessible_ai_insight_queryset(
    user,
    context,
):
    context = require_ai_context(
        user,
        context,
    )

    return (
        AIInsight.objects
        .select_related(
            "student",
            "generated_by",
            "reviewed_by",
            "source_report",
        )
        .filter(
            generated_by=user,
            generated_role=context,
            student__professional_assignments__professional=(
                user
            ),
            student__professional_assignments__professional_role=(
                context
            ),
            student__professional_assignments__is_active=True,
        )
        .distinct()
    )


def get_ai_source_report(
    user,
    context,
    report_id,
):
    context = require_ai_context(
        user,
        context,
    )

    queryset = (
        get_accessible_report_queryset(
            user,
            context,
        )
    )

    return get_object_or_404(
        queryset,
        pk=report_id,
    )
