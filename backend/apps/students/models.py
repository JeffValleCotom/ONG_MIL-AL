from django.db import models
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


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