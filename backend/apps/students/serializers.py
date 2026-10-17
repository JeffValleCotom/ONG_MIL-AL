from django.utils import timezone
from rest_framework import serializers

from .models import Student


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
