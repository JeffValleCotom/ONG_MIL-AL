from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.students.models import Student

from .models import Evaluation


User = get_user_model()


class EvaluationStudentSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Student
        fields = [
            "id",
            "institutional_code",
            "first_name",
            "last_name",
            "is_active",
        ]


class EvaluationUserSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
        ]


class EvaluationSerializer(
    serializers.ModelSerializer
):
    student = EvaluationStudentSummarySerializer(
        read_only=True,
    )

    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
        write_only=True,
    )

    created_by = EvaluationUserSummarySerializer(
        read_only=True,
    )

    updated_by = EvaluationUserSummarySerializer(
        read_only=True,
    )

    evaluation_type = serializers.CharField(
        max_length=120,
        allow_blank=False,
        trim_whitespace=True,
    )

    results = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    observations = serializers.CharField(
        allow_blank=True,
        required=False,
        trim_whitespace=True,
    )

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "student",
            "student_id",
            "evaluation_date",
            "evaluation_type",
            "results",
            "observations",
            "professional_role",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "professional_role",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        evaluation_date = attrs.get(
            "evaluation_date",
            getattr(
                self.instance,
                "evaluation_date",
                None,
            ),
        )

        if (
            evaluation_date is not None
            and evaluation_date > timezone.localdate()
        ):
            raise serializers.ValidationError(
                {
                    "evaluation_date": (
                        "La fecha de la evaluación "
                        "no puede ser futura."
                    )
                }
            )

        if (
            self.instance is not None
            and "student" in attrs
            and attrs["student"].pk
            != self.instance.student_id
        ):
            raise serializers.ValidationError(
                {
                    "student_id": (
                        "No se puede cambiar el estudiante "
                        "de una evaluación."
                    )
                }
            )

        return attrs


class EvaluationRecordSerializer(
    serializers.ModelSerializer
):
    created_by = EvaluationUserSummarySerializer(
        read_only=True,
    )

    updated_by = EvaluationUserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = Evaluation
        fields = [
            "id",
            "evaluation_date",
            "evaluation_type",
            "results",
            "observations",
            "professional_role",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class EvaluationRecordSectionSerializer(
    serializers.Serializer
):
    items = EvaluationRecordSerializer(
        many=True,
        read_only=True,
    )
