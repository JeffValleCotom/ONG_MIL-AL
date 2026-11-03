from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Student,
    StudentDocument,
    StudentFamilyMember,
    StudentIntervention,
    StudentInterventionPlan,
    StudentProfessionalAssignment,
)

from apps.academic.serializers import (
    AcademicRecordSectionSerializer,
)
from apps.psychology.serializers import (
    PsychologicalRecordSectionSerializer,
)
from apps.therapy.serializers import (
    TherapyRecordSectionSerializer,
)
from apps.evaluations.serializers import (
    EvaluationRecordSectionSerializer,
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


class StudentFamilyMemberSerializer(
    serializers.ModelSerializer
):
    student_id = serializers.IntegerField(
        read_only=True,
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
    relationship_detail = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
    address = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    class Meta:
        model = StudentFamilyMember
        fields = [
            "id",
            "student_id",
            "first_name",
            "last_name",
            "relationship",
            "relationship_detail",
            "phone",
            "email",
            "address",
            "is_primary_contact",
            "is_active",
            "deactivated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "is_active",
            "deactivated_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        relationship = attrs.get(
            "relationship",
            getattr(
                self.instance,
                "relationship",
                None,
            ),
        )
        relationship_detail = attrs.get(
            "relationship_detail",
            getattr(
                self.instance,
                "relationship_detail",
                "",
            ),
        )

        relationship_detail = (
            relationship_detail.strip()
            if relationship_detail
            else ""
        )

        if (
            "relationship" in attrs
            and relationship
            != StudentFamilyMember.Relationship.OTRO
            and "relationship_detail" not in attrs
        ):
            relationship_detail = ""

        attrs["relationship_detail"] = (
            relationship_detail
        )

        errors = {}

        if (
            relationship
            == StudentFamilyMember.Relationship.OTRO
            and not relationship_detail
        ):
            errors["relationship_detail"] = (
                "Debe especificar el parentesco cuando "
                "selecciona Otro."
            )

        if (
            relationship
            != StudentFamilyMember.Relationship.OTRO
            and relationship_detail
        ):
            errors["relationship_detail"] = (
                "El detalle de parentesco solo corresponde "
                "cuando el parentesco es Otro."
            )

        student = self.context.get("student")

        is_primary_contact = attrs.get(
            "is_primary_contact",
            getattr(
                self.instance,
                "is_primary_contact",
                False,
            ),
        )

        if (
            self.instance is not None
            and not self.instance.is_active
            and is_primary_contact
        ):
            errors["is_primary_contact"] = (
                "Un familiar inactivo no puede ser "
                "contacto principal."
            )

        if (
            student is not None
            and is_primary_contact
        ):
            primary_contacts = (
                StudentFamilyMember.objects.filter(
                    student=student,
                    is_active=True,
                    is_primary_contact=True,
                )
            )

            if self.instance is not None:
                primary_contacts = (
                    primary_contacts.exclude(
                        pk=self.instance.pk
                    )
                )

            if primary_contacts.exists():
                errors["is_primary_contact"] = (
                    "El estudiante ya posee un contacto "
                    "principal activo."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class StudentDocumentUploadSerializer(
    serializers.ModelSerializer
):
    student_id = serializers.IntegerField(
        read_only=True,
    )

    file = serializers.FileField(
        write_only=True,
    )

    document_type_detail = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

    class Meta:
        model = StudentDocument
        fields = [
            "id",
            "student_id",
            "document_type",
            "document_type_detail",
            "file",
            "original_filename",
            "mime_type",
            "size_bytes",
            "sha256",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "original_filename",
            "mime_type",
            "size_bytes",
            "sha256",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        document_type = attrs.get(
            "document_type",
        )

        document_type_detail = attrs.get(
            "document_type_detail",
            "",
        ).strip()

        if (
            document_type
            == StudentDocument.DocumentType.OTRO
        ):
            if not document_type_detail:
                raise serializers.ValidationError(
                    {
                        "document_type_detail": (
                            "Debe especificar el tipo de "
                            "documento cuando selecciona OTRO."
                        )
                    }
                )
        elif document_type_detail:
            raise serializers.ValidationError(
                {
                    "document_type_detail": (
                        "El detalle solo puede indicarse "
                        "cuando el tipo documental es OTRO."
                    )
                }
            )

        attrs["document_type_detail"] = (
            document_type_detail
        )

        return attrs


class StudentDocumentSerializer(
    serializers.ModelSerializer
):
    document_type_display = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )

    class Meta:
        model = StudentDocument
        fields = [
            "id",
            "document_type",
            "document_type_display",
            "document_type_detail",
            "original_filename",
            "mime_type",
            "size_bytes",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


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


class StudentRecordAssignmentUserSerializer(
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


class StudentInterventionSerializer(
    serializers.ModelSerializer
):
    student_id = serializers.IntegerField(
        read_only=True,
    )

    responsible = StudentRecordAssignmentUserSerializer(
        source="created_by",
        read_only=True,
    )

    updated_by = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    objectives = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    observations = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    class Meta:
        model = StudentIntervention
        fields = [
            "id",
            "student_id",
            "intervention_date",
            "professional_role",
            "objectives",
            "observations",
            "responsible",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_id",
            "professional_role",
            "responsible",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate_intervention_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "La fecha de la intervención no puede ser futura."
            )

        return value


class StudentInterventionPlanSerializer(
    serializers.ModelSerializer
):
    student_id = serializers.IntegerField(
        read_only=True,
    )

    responsible = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    responsible_id = serializers.PrimaryKeyRelatedField(
        source="responsible",
        queryset=User.objects.all(),
        write_only=True,
    )

    responsible_role = serializers.ChoiceField(
        choices=StudentIntervention.ProfessionalRole.choices,
    )

    created_by = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    updated_by = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    objectives = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    class Meta:
        model = StudentInterventionPlan
        fields = [
            "id",
            "student_id",
            "objectives",
            "estimated_start_date",
            "estimated_end_date",
            "professional_role",
            "responsible",
            "responsible_id",
            "responsible_role",
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "student_id",
            "professional_role",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        start_date = attrs.get(
            "estimated_start_date",
            getattr(
                self.instance,
                "estimated_start_date",
                None,
            ),
        )

        end_date = attrs.get(
            "estimated_end_date",
            getattr(
                self.instance,
                "estimated_end_date",
                None,
            ),
        )

        if (
            start_date is not None
            and end_date is not None
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "estimated_end_date": (
                        "La fecha final no puede ser anterior "
                        "a la fecha inicial."
                    )
                }
            )

        new_status = attrs.get(
            "status",
            getattr(
                self.instance,
                "status",
                StudentInterventionPlan.Status.PLANNED,
            ),
        )

        if self.instance is None:
            if (
                new_status
                != StudentInterventionPlan.Status.PLANNED
            ):
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Una planificación nueva debe iniciar "
                            "en estado PLANIFICADA."
                        )
                    }
                )

            return attrs

        allowed_transitions = {
            StudentInterventionPlan.Status.PLANNED: {
                StudentInterventionPlan.Status.PLANNED,
                StudentInterventionPlan.Status.IN_PROGRESS,
                StudentInterventionPlan.Status.CANCELLED,
            },
            StudentInterventionPlan.Status.IN_PROGRESS: {
                StudentInterventionPlan.Status.IN_PROGRESS,
                StudentInterventionPlan.Status.COMPLETED,
                StudentInterventionPlan.Status.CANCELLED,
            },
            StudentInterventionPlan.Status.COMPLETED: {
                StudentInterventionPlan.Status.COMPLETED,
            },
            StudentInterventionPlan.Status.CANCELLED: {
                StudentInterventionPlan.Status.CANCELLED,
            },
        }

        if (
            new_status
            not in allowed_transitions[
                self.instance.status
            ]
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "La transición de estado solicitada "
                        "no es válida."
                    )
                }
            )

        return attrs


class StudentInterventionResponsibleOptionSerializer(
    serializers.Serializer
):
    professional = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    professional_role = serializers.CharField(
        read_only=True,
    )


class StudentInterventionSectionSerializer(
    serializers.Serializer
):
    performed = StudentInterventionSerializer(
        many=True,
        read_only=True,
    )

    planned = StudentInterventionPlanSerializer(
        many=True,
        read_only=True,
    )

    responsible_options = (
        StudentInterventionResponsibleOptionSerializer(
            many=True,
            read_only=True,
        )
    )


class StudentRecordAssignmentSerializer(
    serializers.ModelSerializer
):
    professional = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    assigned_by = StudentRecordAssignmentUserSerializer(
        read_only=True,
    )

    class Meta:
        model = StudentProfessionalAssignment
        fields = [
            "id",
            "professional",
            "professional_role",
            "is_active",
            "assigned_at",
            "unassigned_at",
            "assigned_by",
        ]


class StudentRecordAssignmentsSectionSerializer(
    serializers.Serializer
):
    items = StudentRecordAssignmentSerializer(
        many=True,
        read_only=True,
    )


class StudentRecordFamilySectionSerializer(
    serializers.Serializer
):
    items = StudentFamilyMemberSerializer(
        many=True,
        read_only=True,
    )


class StudentHistoryUserSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField(
        read_only=True,
    )
    username = serializers.CharField(
        read_only=True,
    )
    first_name = serializers.CharField(
        read_only=True,
    )
    last_name = serializers.CharField(
        read_only=True,
    )


class StudentHistoryItemSerializer(
    serializers.Serializer
):
    record_id = serializers.IntegerField(
        read_only=True,
    )
    student_id = serializers.IntegerField(
        read_only=True,
    )
    record_type = serializers.CharField(
        read_only=True,
    )
    area = serializers.CharField(
        read_only=True,
    )
    date = serializers.DateField(
        read_only=True,
    )
    title = serializers.CharField(
        read_only=True,
    )
    details = serializers.DictField(
        read_only=True,
    )
    created_by = StudentHistoryUserSerializer(
        read_only=True,
    )
    updated_by = StudentHistoryUserSerializer(
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        read_only=True,
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
    )


class StudentHistorySectionSerializer(
        serializers.Serializer
    ):
        items = StudentHistoryItemSerializer(
            many=True,
            read_only=True,
        )


class StudentEvolutionEvidenceSerializer(
    serializers.Serializer
):
    field = serializers.CharField(
        read_only=True,
    )
    value = serializers.CharField(
        read_only=True,
    )


class StudentEvolutionRecordSerializer(
    serializers.Serializer
):
    record_id = serializers.IntegerField(
        read_only=True,
    )
    student_id = serializers.IntegerField(
        read_only=True,
    )
    record_type = serializers.CharField(
        read_only=True,
    )
    area = serializers.CharField(
        read_only=True,
    )
    date = serializers.DateField(
        read_only=True,
    )
    title = serializers.CharField(
        read_only=True,
    )
    evidence = StudentEvolutionEvidenceSerializer(
        many=True,
        read_only=True,
    )


class StudentEvolutionSummarySerializer(
    serializers.Serializer
):
    total_records = serializers.IntegerField(
        read_only=True,
    )
    followup_count = serializers.IntegerField(
        read_only=True,
    )
    evaluation_count = serializers.IntegerField(
        read_only=True,
    )
    period_count = serializers.IntegerField(
        read_only=True,
    )
    first_record_date = serializers.DateField(
        read_only=True,
        allow_null=True,
    )
    latest_record_date = serializers.DateField(
        read_only=True,
        allow_null=True,
    )


class StudentEvolutionPeriodSerializer(
    serializers.Serializer
):
    period = serializers.CharField(
        read_only=True,
    )
    total_records = serializers.IntegerField(
        read_only=True,
    )
    followup_count = serializers.IntegerField(
        read_only=True,
    )
    evaluation_count = serializers.IntegerField(
        read_only=True,
    )
    areas = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )
    records = StudentEvolutionRecordSerializer(
        many=True,
        read_only=True,
    )


class StudentEvolutionSectionSerializer(
    serializers.Serializer
):
    summary = StudentEvolutionSummarySerializer(
        read_only=True,
    )
    periods = StudentEvolutionPeriodSerializer(
        many=True,
        read_only=True,
    )


class StudentRecordSectionsSerializer(
    serializers.Serializer
):
    general = StudentRecordGeneralSerializer(
        read_only=True,
    )

    family = StudentRecordFamilySectionSerializer(
        read_only=True,
        required=False,
    )

    assignments = StudentRecordAssignmentsSectionSerializer(
        read_only=True,
        required=False,
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

    evaluations = EvaluationRecordSectionSerializer(
        read_only=True,
        required=False,
    )

    history = StudentHistorySectionSerializer(
        read_only=True,
        required=False,
    )

    evolution = StudentEvolutionSectionSerializer(
        read_only=True,
        required=False,
    )

    interventions = StudentInterventionSectionSerializer(
        read_only=True,
        required=False,
    )


class StudentRecordCapabilitiesSerializer(
    serializers.Serializer
):
    update_general = serializers.BooleanField(
        read_only=True,
    )
    manage_family = serializers.BooleanField(
        read_only=True,
    )
    manage_academic = serializers.BooleanField(
        read_only=True,
    )
    manage_psychological = serializers.BooleanField(
        read_only=True,
    )
    manage_therapy = serializers.BooleanField(
        read_only=True,
    )
    manage_evaluations = serializers.BooleanField(
        read_only=True,
    )
    manage_interventions = serializers.BooleanField(
        read_only=True,
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
    capabilities = StudentRecordCapabilitiesSerializer(
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
