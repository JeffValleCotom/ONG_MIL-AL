from rest_framework import serializers


DASHBOARD_CONTEXTS = (
    "DOCENTE",
    "PSICOLOGO",
    "TERAPEUTA",
    "RESPONSABLE_INSTITUCIONAL",
)


class DashboardQuerySerializer(serializers.Serializer):
    context = serializers.ChoiceField(
        choices=DASHBOARD_CONTEXTS,
        required=False,
        allow_blank=True,
    )

    date_from = serializers.DateField(
        required=False,
    )

    date_to = serializers.DateField(
        required=False,
    )

    def validate(self, attrs):
        date_from = attrs.get("date_from")
        date_to = attrs.get("date_to")

        if (
            date_from
            and date_to
            and date_from > date_to
        ):
            raise serializers.ValidationError(
                {
                    "date_to": (
                        "La fecha final debe ser igual "
                        "o posterior a la fecha inicial."
                    )
                }
            )

        return attrs
