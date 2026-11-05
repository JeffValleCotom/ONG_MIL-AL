import json


from .access import (
    get_ai_source_report,
    get_ai_student,
)
from .context import (
    build_ai_context,
    build_report_ai_context,
)
from .models import AIInsight
from .prompts import (
    PROMPT_VERSION,
    build_system_prompt,
)
from .providers import get_ai_provider
from .schemas import (
    ANALYSIS_SCHEMA,
    FOLLOWUP_SUGGESTION_SCHEMA,
    INTERVENTION_RECOMMENDATION_SCHEMA,
    REPORT_SUGGESTION_SCHEMA,
)


AI_NOTICE = (
    "Contenido generado por inteligencia artificial "
    "como apoyo al análisis profesional. "
    "No constituye diagnóstico ni decisión definitiva."
)


CONFIG_BY_KIND = {
    AIInsight.Kind.ANALYSIS: {
        "schema_name": "student_analysis",
        "schema": ANALYSIS_SCHEMA,
        "max_output_tokens": 1400,
    },
    AIInsight.Kind.FOLLOWUP_SUGGESTION: {
        "schema_name": "followup_suggestions",
        "schema": FOLLOWUP_SUGGESTION_SCHEMA,
        "max_output_tokens": 1400,
    },
    AIInsight.Kind.INTERVENTION_RECOMMENDATION: {
        "schema_name": (
            "intervention_recommendations"
        ),
        "schema": (
            INTERVENTION_RECOMMENDATION_SCHEMA
        ),
        "max_output_tokens": 1600,
    },
    AIInsight.Kind.REPORT_SUGGESTION: {
        "schema_name": "report_suggestions",
        "schema": REPORT_SUGGESTION_SCHEMA,
        "max_output_tokens": 1600,
    },
}


def _review_status_for_kind(kind):
    if kind == AIInsight.Kind.ANALYSIS:
        return (
            AIInsight
            .ReviewStatus
            .NOT_APPLICABLE
        )

    return AIInsight.ReviewStatus.PENDING


def _build_user_prompt(context_snapshot):
    context_json = json.dumps(
        context_snapshot,
        ensure_ascii=False,
        indent=2,
    )

    return (
        "Analiza exclusivamente el siguiente "
        "contexto autorizado.\n\n"
        "CONTEXTO:\n"
        f"{context_json}"
    )

def generate_ai_insight(
    *,
    user,
    context,
    kind,
    student_id=None,
    date_from=None,
    date_to=None,
    source_report_id=None,
):
    try:
        config = CONFIG_BY_KIND[kind]
    except KeyError as exc:
        raise ValueError(
            "Tipo de solicitud de IA "
            "no soportado."
        ) from exc

    source_report = None

    if (
        kind
        == AIInsight.Kind.REPORT_SUGGESTION
    ):
        source_report = (
            get_ai_source_report(
                user,
                context,
                source_report_id,
            )
        )

        student = source_report.student

        context_snapshot = (
            build_report_ai_context(
                source_report
            )
        )

        date_from = source_report.date_from
        date_to = source_report.date_to
    else:
        student = get_ai_student(
            user,
            context,
            student_id,
        )

        context_snapshot = (
            build_ai_context(
                student=student,
                context=context,
                date_from=date_from,
                date_to=date_to,
            )
        )

    system_prompt = build_system_prompt(
        kind=kind,
        professional_context=context,
    )

    user_prompt = _build_user_prompt(
        context_snapshot
    )

    provider = get_ai_provider()

    provider_result = (
        provider.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema_name=(
                config["schema_name"]
            ),
            schema=config["schema"],
            max_output_tokens=(
                config["max_output_tokens"]
            ),
        )
    )

    result_json = {
        **provider_result.data,
        "ai_notice": AI_NOTICE,
    }

    insight = AIInsight.objects.create(
        student=student,
        source_report=source_report,
        kind=kind,
        date_from=date_from,
        date_to=date_to,
        generated_role=context,
        context_snapshot=context_snapshot,
        result_json=result_json,
        provider=provider_result.provider,
        model_name=provider_result.model,
        provider_response_id=(
            provider_result.response_id
            or ""
        ),
        usage_json=provider_result.usage,
        prompt_version=PROMPT_VERSION,
        generated_by=user,
        review_status=(
            _review_status_for_kind(kind)
        ),
    )

    return insight
