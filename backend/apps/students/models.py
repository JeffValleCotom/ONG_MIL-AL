from pathlib import Path
from uuid import uuid4

from django.db import models
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .storage import private_student_document_storage


class Student(models.Model):
    institutional_code = models.CharField(
        max_length=30,
        unique=True,
    )
    first_name = models.CharField(
        max_length=100,
    )
    last_name = models.CharField(
        max_length=100,
    )
    date_of_birth = models.DateField()
    admission_date = models.DateField()
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.institutional_code} - "
            f"{self.first_name} {self.last_name}"
        )


class StudentProfessionalAssignment(models.Model):
    class ProfessionalRole(models.TextChoices):
        DOCENTE = "DOCENTE", "Docente"
        PSICOLOGO = "PSICOLOGO", "Psicólogo"
        TERAPEUTA = "TERAPEUTA", "Terapeuta"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="professional_assignments",
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_assignments",
    )
    professional_role = models.CharField(
        max_length=20,
        choices=ProfessionalRole.choices,
    )
    is_active = models.BooleanField(
        default=True,
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
    )
    unassigned_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_assignments_created",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-assigned_at",
            "-id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "professional",
                    "professional_role",
                ],
                condition=Q(is_active=True),
                name="uniq_active_student_prof_role",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        is_active=True,
                        unassigned_at__isnull=True,
                    )
                    | Q(
                        is_active=False,
                        unassigned_at__isnull=False,
                    )
                ),
                name="student_assignment_status_dates_ck",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.professional.username} - "
            f"{self.professional_role}"
        )


class StudentFamilyMember(models.Model):
    class Relationship(models.TextChoices):
        MADRE = "MADRE", "Madre"
        PADRE = "PADRE", "Padre"
        HERMANO_A = "HERMANO_A", "Hermano/a"
        ABUELO_A = "ABUELO_A", "Abuelo/a"
        TIO_A = "TIO_A", "Tío/a"
        TUTOR = "TUTOR", "Tutor"
        CUIDADOR = "CUIDADOR", "Cuidador"
        OTRO = "OTRO", "Otro"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="family_members",
    )
    first_name = models.CharField(
        max_length=100,
    )
    last_name = models.CharField(
        max_length=100,
    )
    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
    )
    relationship_detail = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )
    email = models.EmailField(
        blank=True,
        default="",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    is_primary_contact = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="family_members_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="family_members_updated",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-is_active",
            "-is_primary_contact",
            "last_name",
            "first_name",
            "id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                ],
                condition=Q(
                    is_active=True,
                    is_primary_contact=True,
                ),
                name="uniq_active_primary_family_contact",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        is_active=True,
                        deactivated_at__isnull=True,
                    )
                    | Q(
                        is_active=False,
                        deactivated_at__isnull=False,
                    )
                ),
                name="student_family_status_dates_ck",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        relationship="OTRO",
                    )
                    & ~Q(
                        relationship_detail="",
                    )
                    | ~Q(
                        relationship="OTRO",
                    )
                    & Q(
                        relationship_detail="",
                    )
                ),
                name="student_family_relationship_detail_ck",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.first_name} {self.last_name} - "
            f"{self.relationship}"
        )


def student_document_upload_to(instance, filename):
    extension = Path(filename).suffix.lower()
    now = timezone.now()

    physical_name = f"{uuid4().hex}{extension}"

    return (
        f"students/{instance.student_id}/documents/"
        f"{now.year:04d}/{now.month:02d}/{physical_name}"
    )


class StudentDocument(models.Model):

    class DocumentType(models.TextChoices):
        IDENTIFICACION = (
            "IDENTIFICACION",
            "Documento de identificación",
        )
        CONSENTIMIENTO_AUTORIZACION = (
            "CONSENTIMIENTO_AUTORIZACION",
            "Consentimiento o autorización",
        )
        ACADEMICO = (
            "ACADEMICO",
            "Documento académico",
        )
        MEDICO = (
            "MEDICO",
            "Documento médico",
        )
        PSICOLOGICO = (
            "PSICOLOGICO",
            "Documento psicológico",
        )
        TERAPEUTICO = (
            "TERAPEUTICO",
            "Documento terapéutico",
        )
        INSTITUCIONAL = (
            "INSTITUCIONAL",
            "Documento institucional",
        )
        OTRO = (
            "OTRO",
            "Otro documento",
        )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
    )

    document_type_detail = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    original_filename = models.CharField(
        max_length=255,
    )

    file = models.FileField(
        upload_to=student_document_upload_to,
        storage=private_student_document_storage,
        max_length=500,
    )

    mime_type = models.CharField(
        max_length=100,
    )

    size_bytes = models.PositiveBigIntegerField()

    sha256 = models.CharField(
        max_length=64,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_documents_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_documents_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-is_active",
            "-created_at",
            "-id",
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        is_active=True,
                        deactivated_at__isnull=True,
                    )
                    | Q(
                        is_active=False,
                        deactivated_at__isnull=False,
                    )
                ),
                name="student_document_status_dates_ck",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        document_type="OTRO",
                    )
                    & ~Q(
                        document_type_detail="",
                    )
                    | ~Q(
                        document_type="OTRO",
                    )
                    & Q(
                        document_type_detail="",
                    )
                ),
                name="student_document_type_detail_ck",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student.institutional_code} - "
            f"{self.document_type} - "
            f"{self.original_filename}"
        )
