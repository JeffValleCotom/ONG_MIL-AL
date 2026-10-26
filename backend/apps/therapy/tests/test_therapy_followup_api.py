from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)
from apps.therapy.models import TherapyFollowUp


User = get_user_model()


class TherapyFollowUpAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.psychologist_group = Group.objects.get(
            name="PSICOLOGO",
        )
        cls.therapist_group = Group.objects.get(
            name="TERAPEUTA",
        )
        cls.responsible_group = Group.objects.get(
            name="RESPONSABLE_INSTITUCIONAL",
        )

        cls.therapist = User.objects.create_user(
            username="therapy_test",
            password="test-password",
        )
        cls.therapist.groups.add(
            cls.therapist_group,
        )

        cls.other_therapist = User.objects.create_user(
            username="therapy_other_test",
            password="test-password",
        )
        cls.other_therapist.groups.add(
            cls.therapist_group,
        )

        cls.psychologist = User.objects.create_user(
            username="therapy_psych_test",
            password="test-password",
        )
        cls.psychologist.groups.add(
            cls.psychologist_group,
        )

        cls.multi_role_user = User.objects.create_user(
            username="therapy_multi_test",
            password="test-password",
        )
        cls.multi_role_user.groups.add(
            cls.psychologist_group,
            cls.therapist_group,
        )

        cls.responsible = User.objects.create_user(
            username="responsible_therapy_test",
            password="test-password",
        )
        cls.responsible.groups.add(
            cls.responsible_group,
        )

        cls.assigned_student = Student.objects.create(
            institutional_code="MIL-TH-001",
            first_name="Ana",
            last_name="Terapia",
            date_of_birth=date(2012, 4, 10),
            admission_date=date(2025, 4, 10),
            is_active=True,
        )

        cls.unassigned_student = Student.objects.create(
            institutional_code="MIL-TH-002",
            first_name="Mario",
            last_name="NoAsignado",
            date_of_birth=date(2013, 5, 10),
            admission_date=date(2025, 5, 10),
            is_active=True,
        )

        cls.inactive_student = Student.objects.create(
            institutional_code="MIL-TH-003",
            first_name="Sofia",
            last_name="Inactiva",
            date_of_birth=date(2011, 6, 10),
            admission_date=date(2025, 6, 10),
            is_active=False,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.assigned_student,
            professional=cls.therapist,
            professional_role="TERAPEUTA",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.unassigned_student,
            professional=cls.other_therapist,
            professional_role="TERAPEUTA",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.inactive_student,
            professional=cls.therapist,
            professional_role="TERAPEUTA",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.assigned_student,
            professional=cls.multi_role_user,
            professional_role="TERAPEUTA",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.assigned_student,
            professional=cls.multi_role_user,
            professional_role="PSICOLOGO",
            assigned_by=cls.responsible,
            is_active=True,
        )

        cls.assigned_followup = TherapyFollowUp.objects.create(
            student=cls.assigned_student,
            followup_date=date(2026, 1, 15),
            therapy_area="Terapia ocupacional",
            objectives="Fortalecer autonomía.",
            activities="Actividades funcionales.",
            progress_notes="Progreso favorable.",
            recommendations="Continuar ejercicios.",
            created_by=cls.therapist,
            updated_by=cls.therapist,
        )

        cls.unassigned_followup = TherapyFollowUp.objects.create(
            student=cls.unassigned_student,
            followup_date=date(2026, 1, 16),
            therapy_area="Lenguaje",
            objectives="Seguimiento.",
            progress_notes="No debe ser visible.",
            created_by=cls.other_therapist,
            updated_by=cls.other_therapist,
        )

    def authenticate(self, user):
        self.client.force_authenticate(
            user=user,
        )

    def therapy_context_url(self):
        return (
            f"{reverse('therapy-followup-list')}"
            "?context=TERAPEUTA"
        )

    def test_list_only_returns_assigned_students(self):
        self.authenticate(self.therapist)

        response = self.client.get(
            self.therapy_context_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in response.data
        }

        self.assertIn(
            self.assigned_followup.id,
            returned_ids,
        )

        self.assertNotIn(
            self.unassigned_followup.id,
            returned_ids,
        )

    def test_unassigned_followup_detail_returns_404(self):
        self.authenticate(self.therapist)

        url = reverse(
            "therapy-followup-detail",
            kwargs={
                "pk": self.unassigned_followup.pk,
            },
        )

        response = self.client.get(
            f"{url}?context=TERAPEUTA",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_assigned_followup(self):
        self.authenticate(self.therapist)

        response = self.client.post(
            self.therapy_context_url(),
            {
                "student_id": self.assigned_student.pk,
                "followup_date": "2026-02-01",
                "therapy_area": "Terapia ocupacional",
                "objectives": "Fortalecer coordinación.",
                "activities": "Ejercicios funcionales.",
                "progress_notes": "Respuesta adecuada.",
                "recommendations": "Continuar ejercicios.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        followup = TherapyFollowUp.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            followup.student,
            self.assigned_student,
        )
        self.assertEqual(
            followup.created_by,
            self.therapist,
        )
        self.assertEqual(
            followup.updated_by,
            self.therapist,
        )

    def test_create_for_unassigned_student_returns_404(self):
        self.authenticate(self.therapist)

        response = self.client.post(
            self.therapy_context_url(),
            {
                "student_id": self.unassigned_student.pk,
                "followup_date": "2026-02-01",
                "therapy_area": "No autorizada",
                "objectives": "No debe crearse.",
                "progress_notes": "No debe crearse.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_for_inactive_student_returns_400(self):
        self.authenticate(self.therapist)

        response = self.client.post(
            self.therapy_context_url(),
            {
                "student_id": self.inactive_student.pk,
                "followup_date": "2026-02-01",
                "therapy_area": "Seguimiento",
                "objectives": "No debe crearse.",
                "progress_notes": "No debe crearse.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_future_followup_date_returns_400(self):
        self.authenticate(self.therapist)

        future_date = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.therapy_context_url(),
            {
                "student_id": self.assigned_student.pk,
                "followup_date": future_date.isoformat(),
                "therapy_area": "Seguimiento",
                "objectives": "Validar fecha.",
                "progress_notes": "Fecha inválida.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_missing_context_returns_400(self):
        self.authenticate(self.therapist)

        response = self.client.get(
            reverse("therapy-followup-list"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_psychologist_cannot_access_therapy(self):
        self.authenticate(self.psychologist)

        response = self.client.get(
            self.therapy_context_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_multi_role_wrong_context_is_forbidden(self):
        self.authenticate(self.multi_role_user)

        response = self.client.get(
            (
                f"{reverse('therapy-followup-list')}"
                "?context=PSICOLOGO"
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_updates_followup(self):
        self.authenticate(self.therapist)

        url = reverse(
            "therapy-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.patch(
            f"{url}?context=TERAPEUTA",
            {
                "progress_notes": (
                    "Progreso terapéutico actualizado."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_followup.refresh_from_db()

        self.assertEqual(
            self.assigned_followup.progress_notes,
            "Progreso terapéutico actualizado.",
        )

    def test_patch_cannot_change_student(self):
        self.authenticate(self.therapist)

        url = reverse(
            "therapy-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.patch(
            f"{url}?context=TERAPEUTA",
            {
                "student_id": self.unassigned_student.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_is_not_allowed(self):
        self.authenticate(self.therapist)

        url = reverse(
            "therapy-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.delete(
            f"{url}?context=TERAPEUTA",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
