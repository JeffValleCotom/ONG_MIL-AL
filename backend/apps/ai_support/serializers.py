from rest_framework import serializers

from .models import AIInsight


def validate_period(
    date_from,
    date_to,
):
    if (
        date_from
        and date_to
        and date_to < date_from
    ):
        raise serializers.ValidationError(
            {
                "date_to": (
                    "La fecha final no puede "
                    "ser anterior a la inicial."
                )
            }
        )


class AIInsightStudentSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()
    institutional_code = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class AIInsightListSerializer(
    serializers.ModelSerializer
):
    student = AIInsightStudentSerializer(
        read_only=True,
    )

    class Meta:
        model = AIInsight
        fields = [
            "id",
            "student",
            "source_report",
            "kind",
            "date_from",
            "date_to",
            "generated_role",
            "provider",
            "model_name",
            "prompt_version",
            "review_status",
            "created_at",
            "updated_at",
        ]


class AIInsightDetailSerializer(
    AIInsightListSerializer
):
    class Meta(
        AIInsightListSerializer.Meta
    ):
        fields = (
            AIInsightListSerializer
            .Meta
            .fields
            + [
                "context_snapshot",
                "result_json",
                "professional_notes",
                "edited_content",
                "reviewed_at",
            ]
        )


class AIInsightCreateSerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    source_report_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    kind = serializers.ChoiceField(
        choices=AIInsight.Kind.choices,
    )

    date_from = serializers.DateField(
        required=False,
        allow_null=True,
    )

    date_to = serializers.DateField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        validate_period(
            attrs.get("date_from"),
            attrs.get("date_to"),
        )

        kind = attrs.get("kind")
        student_id = attrs.get(
            "student_id"
        )
        source_report_id = attrs.get(
            "source_report_id"
        )

        if (
            kind
            == AIInsight.Kind.REPORT_SUGGESTION
        ):
            if not source_report_id:
                raise serializers.ValidationError(
                    {
                        "source_report_id": (
                            "Debes indicar el reporte "
                            "que será asistido por IA."
                        )
                    }
                )

            if (
                attrs.get("date_from")
                or attrs.get("date_to")
            ):
                raise serializers.ValidationError(
                    {
                        "date_from": (
                            "Las sugerencias para "
                            "reportes utilizan el "
                            "período del reporte "
                            "original."
                        )
                    }
                )

            return attrs

        if not student_id:
            raise serializers.ValidationError(
                {
                    "student_id": (
                        "Debes indicar el "
                        "estudiante."
                    )
                }
            )

        if source_report_id:
            raise serializers.ValidationError(
                {
                    "source_report_id": (
                        "El reporte origen solo "
                        "puede utilizarse para "
                        "sugerencias de reporte."
                    )
                }
            )

        return attrs


class AIInsightReviewSerializer(
    serializers.Serializer
):
    decision = serializers.ChoiceField(
        choices=[
            AIInsight.ReviewStatus.ACCEPTED,
            AIInsight.ReviewStatus.DISCARDED,
            AIInsight.ReviewStatus.IGNORED,
        ],
    )

    professional_notes = (
        serializers.CharField(
            required=False,
            allow_blank=True,
            max_length=4000,
        )
    )

    edited_content = serializers.JSONField(
        required=False,
        allow_null=True,
    )


class AIInsightFilterSerializer(
    serializers.Serializer
):
    student = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    source_report = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    kind = serializers.ChoiceField(
        required=False,
        choices=AIInsight.Kind.choices,
    )

    review_status = serializers.ChoiceField(
        required=False,
        choices=AIInsight.ReviewStatus.choices,
    )

    date_from = serializers.DateField(
        required=False,
    )

    date_to = serializers.DateField(
        required=False,
    )

    def validate(self, attrs):
        validate_period(
            attrs.get("date_from"),
            attrs.get("date_to"),
        )

        return attrs
