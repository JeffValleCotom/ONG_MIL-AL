from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.students.models import Student

from .models import AcademicFollowUp


User = get_user_model()


class AcademicStudentSummarySerializer(
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


class AcademicUserSummarySerializer(
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


class AcademicFollowUpSerializer(
    serializers.ModelSerializer
):
    student = AcademicStudentSummarySerializer(
        read_only=True,
    )

    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
        write_only=True,
    )

    created_by = AcademicUserSummarySerializer(
        read_only=True,
    )

    updated_by = AcademicUserSummarySerializer(
        read_only=True,
    )

    academic_period = serializers.CharField(
        max_length=50,
        allow_blank=False,
        trim_whitespace=True,
    )

    subject = serializers.CharField(
        max_length=120,
        allow_blank=False,
        trim_whitespace=True,
    )

    observations = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    class Meta:
        model = AcademicFollowUp
        fields = [
            "id",
            "student",
            "student_id",
            "followup_date",
            "academic_period",
            "subject",
            "observations",
            "strengths",
            "areas_for_improvement",
            "recommendations",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        followup_date = attrs.get(
            "followup_date",
            getattr(
                self.instance,
                "followup_date",
                None,
            ),
        )

        if (
            followup_date is not None
            and followup_date > timezone.localdate()
        ):
            raise serializers.ValidationError(
                {
                    "followup_date": (
                        "La fecha del seguimiento "
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
                        "de un seguimiento académico."
                    )
                }
            )

        return attrs


class AcademicFollowUpRecordSerializer(
    serializers.ModelSerializer
):
    created_by = AcademicUserSummarySerializer(
        read_only=True,
    )

    updated_by = AcademicUserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = AcademicFollowUp
        fields = [
            "id",
            "followup_date",
            "academic_period",
            "subject",
            "observations",
            "strengths",
            "areas_for_improvement",
            "recommendations",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class AcademicRecordSectionSerializer(
    serializers.Serializer
):
    followups = AcademicFollowUpRecordSerializer(
        many=True,
        read_only=True,
    )
