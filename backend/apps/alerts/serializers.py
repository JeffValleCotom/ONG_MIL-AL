from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.students.models import (
    Student,
    StudentInterventionPlan,
)

from .models import Alert, AlertEvent


User = get_user_model()


class AlertQuerySerializer(serializers.Serializer):
    context = serializers.ChoiceField(
        choices=(
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
            "RESPONSABLE_INSTITUCIONAL",
        ),
        required=False,
        allow_blank=True,
    )

    status = serializers.ChoiceField(
        choices=Alert.Status.choices,
        required=False,
        allow_blank=True,
    )


class AlertUserSerializer(
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


class AlertStudentSerializer(
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


class AlertPlanSerializer(
    serializers.ModelSerializer
):
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = StudentInterventionPlan
        fields = [
            "id",
            "estimated_start_date",
            "estimated_end_date",
            "professional_role",
            "responsible_role",
            "status",
            "status_label",
        ]


class AlertEventSerializer(
    serializers.ModelSerializer
):
    performed_by = AlertUserSerializer(
        read_only=True,
    )

    event_type_label = serializers.CharField(
        source="get_event_type_display",
        read_only=True,
    )

    class Meta:
        model = AlertEvent
        fields = [
            "id",
            "event_type",
            "event_type_label",
            "from_status",
            "to_status",
            "performed_by",
            "note",
            "created_at",
        ]


class AlertSerializer(
    serializers.ModelSerializer
):
    student = AlertStudentSerializer(
        read_only=True,
    )

    intervention_plan = AlertPlanSerializer(
        read_only=True,
    )

    assigned_to = AlertUserSerializer(
        read_only=True,
    )

    reviewed_by = AlertUserSerializer(
        read_only=True,
    )

    resolved_by = AlertUserSerializer(
        read_only=True,
    )

    history = AlertEventSerializer(
        many=True,
        read_only=True,
    )

    condition_label = serializers.CharField(
        source="get_condition_display",
        read_only=True,
    )

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Alert
        fields = [
            "id",
            "condition",
            "condition_label",
            "student",
            "intervention_plan",
            "assigned_to",
            "assigned_role",
            "reason",
            "status",
            "status_label",
            "detected_at",
            "reviewed_by",
            "reviewed_at",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
            "history",
        ]
