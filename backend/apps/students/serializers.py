from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Student, StudentProfessionalAssignment

from apps.academic.serializers import (
    AcademicRecordSectionSerializer,
)
from apps.psychology.serializers import (
    PsychologicalRecordSectionSerializer,
)
from apps.therapy.serializers import (
    TherapyRecordSectionSerializer,
)

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    institutional_code = serializers.CharField(
        max_length=30,
        allow_blank=False,
        trim_whitespace=True,
        validators=[],
    )
    first_name = serializers.CharField(
        max_length=100,
        allow_blank=False,
        trim_whitespace=True,
    )
    last_name = serializers.CharField(
        max_length=100,
        allow_blank=False,
        trim_whitespace=True,
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "institutional_code",
            "first_name",
            "last_name",
            "date_of_birth",
            "admission_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_institutional_code(self, value):
        normalized_code = value.strip().upper()

        if not normalized_code:
            raise serializers.ValidationError(
                "El código institucional es obligatorio."
            )

        students = Student.objects.filter(
            institutional_code=normalized_code
        )

        if self.instance is not None:
            students = students.exclude(
                pk=self.instance.pk
            )

        if students.exists():
            raise serializers.ValidationError(
                "Ya existe un estudiante con este código institucional."
            )

        return normalized_code

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if (
            self.instance is not None
            and "is_active" in self.initial_data
        ):
            raise serializers.ValidationError(
                {
                    "is_active": (
                        "El estado del estudiante debe "
                        "modificarse mediante las acciones "
                        "de activación o desactivación."
                    )
                }
            )

        date_of_birth = attrs.get(
            "date_of_birth",
            getattr(
                self.instance,
                "date_of_birth",
                None,
            ),
        )
        admission_date = attrs.get(
            "admission_date",
            getattr(
                self.instance,
                "admission_date",
                None,
            ),
        )

        today = timezone.localdate()
        errors = {}

        if (
            date_of_birth is not None
            and date_of_birth > today
        ):
            errors["date_of_birth"] = (
                "La fecha de nacimiento no puede ser futura."
            )

        if (
            admission_date is not None
            and admission_date > today
        ):
            errors["admission_date"] = (
                "La fecha de ingreso no puede ser futura."
            )

        if (
            date_of_birth is not None
            and admission_date is not None
            and admission_date < date_of_birth
        ):
            errors["admission_date"] = (
                "La fecha de ingreso no puede ser anterior "
                "a la fecha de nacimiento."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class StudentRecordGeneralSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Student
        fields = [
            "institutional_code",
            "first_name",
            "last_name",
            "date_of_birth",
            "admission_date",
            "is_active",
        ]


class StudentRecordSectionsSerializer(
    serializers.Serializer
):
    general = StudentRecordGeneralSerializer(
        read_only=True,
    )

    academic = AcademicRecordSectionSerializer(
        read_only=True,
        required=False,
    )

    psychological = PsychologicalRecordSectionSerializer(
        read_only=True,
        required=False,
    )

    therapy = TherapyRecordSectionSerializer(
        read_only=True,
        required=False,
    )


class StudentRecordSerializer(
    serializers.Serializer
):
    student_id = serializers.IntegerField(
        read_only=True,
    )
    context = serializers.CharField(
        read_only=True,
    )
    sections = StudentRecordSectionsSerializer(
        read_only=True,
    )


class AssignmentUserSummarySerializer(
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


class AssignmentStudentSummarySerializer(
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


class StudentProfessionalAssignmentSerializer(
    serializers.ModelSerializer
):
    student = AssignmentStudentSummarySerializer(
        read_only=True,
    )
    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=Student.objects.all(),
        write_only=True,
    )

    professional = AssignmentUserSummarySerializer(
        read_only=True,
    )
    professional_id = serializers.PrimaryKeyRelatedField(
        source="professional",
        queryset=User.objects.all(),
        write_only=True,
    )

    assigned_by = AssignmentUserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = StudentProfessionalAssignment
        fields = [
            "id",
            "student",
            "student_id",
            "professional",
            "professional_id",
            "professional_role",
            "is_active",
            "assigned_at",
            "unassigned_at",
            "assigned_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "assigned_at",
            "unassigned_at",
            "assigned_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        student = attrs["student"]
        professional = attrs["professional"]
        professional_role = attrs["professional_role"]

        errors = {}

        if not student.is_active:
            errors["student_id"] = (
                "No se puede asignar un profesional "
                "a un estudiante inactivo."
            )

        if not professional.is_active:
            errors["professional_id"] = (
                "El profesional seleccionado está inactivo."
            )
        elif not professional.groups.filter(
            name=professional_role,
        ).exists():
            errors["professional_id"] = (
                "El usuario seleccionado no posee "
                f"el rol {professional_role}."
            )

        if StudentProfessionalAssignment.objects.filter(
            student=student,
            professional=professional,
            professional_role=professional_role,
            is_active=True,
        ).exists():
            errors["non_field_errors"] = (
                "Ya existe una asignación activa para "
                "este estudiante, profesional y rol."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
