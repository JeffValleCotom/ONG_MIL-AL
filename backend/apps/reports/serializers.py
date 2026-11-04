from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.students.models import Student

from .models import StudentReport


User = get_user_model()


class ReportStudentSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Student
        fields = [
            "id",
            "institutional_code",
            "first_name",
            "last_name",
        ]


class ReportUserSerializer(
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


class StudentReportListSerializer(
    serializers.ModelSerializer
):
    student = ReportStudentSerializer(
        read_only=True,
    )

    generated_by = ReportUserSerializer(
        read_only=True,
    )

    class Meta:
        model = StudentReport
        fields = [
            "id",
            "student",
            "report_type",
            "date_from",
            "date_to",
            "generated_role",
            "generated_by",
            "generated_at",
        ]

        read_only_fields = fields


class StudentReportSerializer(
    StudentReportListSerializer
):
    class Meta(
        StudentReportListSerializer.Meta
    ):
        fields = [
            *StudentReportListSerializer.Meta.fields,
            "content_snapshot",
        ]


def validate_report_period(attrs):
    date_from = attrs.get("date_from")
    date_to = attrs.get("date_to")

    if (
        date_from
        and date_to
        and date_to < date_from
    ):
        raise serializers.ValidationError(
            {
                "date_to": (
                    "La fecha final no puede ser anterior "
                    "a la fecha inicial."
                )
            }
        )

    return attrs


class StudentReportCreateSerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField(
        min_value=1,
    )

    report_type = serializers.ChoiceField(
        choices=StudentReport.ReportType.choices,
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
        return validate_report_period(attrs)


class StudentReportFilterSerializer(
    serializers.Serializer
):
    student = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    report_type = serializers.ChoiceField(
        choices=StudentReport.ReportType.choices,
        required=False,
    )

    date_from = serializers.DateField(
        required=False,
    )

    date_to = serializers.DateField(
        required=False,
    )

    def validate(self, attrs):
        return validate_report_period(attrs)
