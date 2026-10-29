from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)


User = get_user_model()


class PsychologicalFollowUpAPITests(APITestCase):
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

        cls.psychologist = User.objects.create_user(
            username="psych_test",
            password="test-password",
        )
        cls.psychologist.groups.add(
            cls.psychologist_group,
        )

        cls.other_psychologist = User.objects.create_user(
            username="psych_other_test",
            password="test-password",
        )
        cls.other_psychologist.groups.add(
            cls.psychologist_group,
        )

        cls.therapist = User.objects.create_user(
            username="therapist_test",
            password="test-password",
        )
        cls.therapist.groups.add(
            cls.therapist_group,
        )

        cls.multi_role_user = User.objects.create_user(
            username="psych_multi_test",
            password="test-password",
        )
        cls.multi_role_user.groups.add(
            cls.psychologist_group,
            cls.therapist_group,
        )

        cls.responsible = User.objects.create_user(
            username="responsible_psych_test",
            password="test-password",
        )
        cls.responsible.groups.add(
            cls.responsible_group,
        )

        cls.assigned_student = Student.objects.create(
            institutional_code="MIL-PSY-001",
            first_name="Ana",
            last_name="Psicologia",
            date_of_birth=date(2012, 1, 10),
            admission_date=date(2025, 1, 10),
            is_active=True,
        )

        cls.unassigned_student = Student.objects.create(
            institutional_code="MIL-PSY-002",
            first_name="Carlos",
            last_name="NoAsignado",
            date_of_birth=date(2013, 2, 10),
            admission_date=date(2025, 2, 10),
            is_active=True,
        )

        cls.inactive_student = Student.objects.create(
            institutional_code="MIL-PSY-003",
            first_name="Lucia",
            last_name="Inactiva",
            date_of_birth=date(2011, 3, 10),
            admission_date=date(2025, 3, 10),
            is_active=False,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.assigned_student,
            professional=cls.psychologist,
            professional_role="PSICOLOGO",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.unassigned_student,
            professional=cls.other_psychologist,
            professional_role="PSICOLOGO",
            assigned_by=cls.responsible,
            is_active=True,
        )

        StudentProfessionalAssignment.objects.create(
            student=cls.inactive_student,
            professional=cls.psychologist,
            professional_role="PSICOLOGO",
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

        StudentProfessionalAssignment.objects.create(
            student=cls.assigned_student,
            professional=cls.multi_role_user,
            professional_role="TERAPEUTA",
            assigned_by=cls.responsible,
            is_active=True,
        )

        cls.assigned_followup = (
            PsychologicalFollowUp.objects.create(
                student=cls.assigned_student,
                followup_date=date(2026, 1, 15),
                reason="Seguimiento emocional",
                observations="Observaciones iniciales.",
                emotional_behavioral_notes=(
                    "Notas emocionales."
                ),
                recommendations="Mantener seguimiento.",
                created_by=cls.psychologist,
                updated_by=cls.psychologist,
            )
        )

        cls.unassigned_followup = (
            PsychologicalFollowUp.objects.create(
                student=cls.unassigned_student,
                followup_date=date(2026, 1, 16),
                reason="Seguimiento externo",
                observations="No debe ser visible.",
                created_by=cls.other_psychologist,
                updated_by=cls.other_psychologist,
            )
        )

    def authenticate(self, user):
        self.client.force_authenticate(
            user=user,
        )

    def psychological_context_url(self):
        return (
            f"{reverse('psychological-followup-list')}"
            "?context=PSICOLOGO"
        )

    def test_list_only_returns_assigned_students(self):
        self.authenticate(self.psychologist)

        response = self.client.get(
            self.psychological_context_url(),
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
        self.authenticate(self.psychologist)

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.unassigned_followup.pk,
            },
        )

        response = self.client.get(
            f"{url}?context=PSICOLOGO",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_assigned_followup(self):
        self.authenticate(self.psychologist)

        payload = {
            "student_id": self.assigned_student.pk,
            "followup_date": "2026-02-01",
            "reason": "Control psicológico",
            "observations": "Seguimiento estable.",
            "emotional_behavioral_notes": (
                "Sin cambios relevantes."
            ),
            "recommendations": "Continuar control.",
        }

        response = self.client.post(
            self.psychological_context_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        followup = PsychologicalFollowUp.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            followup.student,
            self.assigned_student,
        )
        self.assertEqual(
            followup.created_by,
            self.psychologist,
        )
        self.assertEqual(
            followup.updated_by,
            self.psychologist,
        )

    def test_create_for_unassigned_student_returns_404(self):
        self.authenticate(self.psychologist)

        response = self.client.post(
            self.psychological_context_url(),
            {
                "student_id": self.unassigned_student.pk,
                "followup_date": "2026-02-01",
                "reason": "No autorizado",
                "observations": "No debe crearse.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_for_inactive_student_returns_400(self):
        self.authenticate(self.psychologist)

        response = self.client.post(
            self.psychological_context_url(),
            {
                "student_id": self.inactive_student.pk,
                "followup_date": "2026-02-01",
                "reason": "Estudiante inactivo",
                "observations": "No debe crearse.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_future_followup_date_returns_400(self):
        self.authenticate(self.psychologist)

        future_date = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.psychological_context_url(),
            {
                "student_id": self.assigned_student.pk,
                "followup_date": future_date.isoformat(),
                "reason": "Fecha futura",
                "observations": "Fecha inválida.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_missing_context_returns_400(self):
        self.authenticate(self.psychologist)

        response = self.client.get(
            reverse("psychological-followup-list"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_therapist_cannot_access_psychology(self):
        self.authenticate(self.therapist)

        response = self.client.get(
            self.psychological_context_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_multi_role_wrong_context_is_forbidden(self):
        self.authenticate(self.multi_role_user)

        response = self.client.get(
            (
                f"{reverse('psychological-followup-list')}"
                "?context=TERAPEUTA"
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_patch_updates_followup(self):
        self.authenticate(self.psychologist)

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.patch(
            f"{url}?context=PSICOLOGO",
            {
                "observations": (
                    "Observaciones actualizadas."
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
            self.assigned_followup.observations,
            "Observaciones actualizadas.",
        )

    def test_view_permission_does_not_allow_update(self):
        self.psychologist_group.permissions.remove(
            Permission.objects.get(
                codename="manage_psychological_followups",
            )
        )

        self.authenticate(self.psychologist)

        list_response = self.client.get(
            self.psychological_context_url()
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in list_response.data
        }

        self.assertIn(
            self.assigned_followup.id,
            returned_ids,
        )

        original_observations = (
            self.assigned_followup.observations
        )

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        patch_response = self.client.patch(
            f"{url}?context=PSICOLOGO",
            {
                "observations": (
                    "No debe permitirse esta actualización."
                ),
            },
            format="json",
        )

        self.assertEqual(
            patch_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assigned_followup.refresh_from_db()

        self.assertEqual(
            self.assigned_followup.observations,
            original_observations,
        )

    def test_patch_cannot_change_student(self):
        self.authenticate(self.psychologist)

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.patch(
            f"{url}?context=PSICOLOGO",
            {
                "student_id": self.unassigned_student.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_inactive_assignment_revokes_followup_access(
        self,
    ):
        assignment = (
            StudentProfessionalAssignment.objects.get(
                student=self.assigned_student,
                professional=self.psychologist,
                professional_role="PSICOLOGO",
                is_active=True,
            )
        )

        assignment.is_active = False
        assignment.unassigned_at = timezone.now()
        assignment.save(
            update_fields=[
                "is_active",
                "unassigned_at",
            ]
        )

        self.authenticate(self.psychologist)

        list_response = self.client.get(
            self.psychological_context_url()
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            list_response.data,
            [],
        )

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        detail_response = self.client.get(
            f"{url}?context=PSICOLOGO"
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_is_not_allowed(self):
        self.authenticate(self.psychologist)

        url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": self.assigned_followup.pk,
            },
        )

        response = self.client.delete(
            f"{url}?context=PSICOLOGO",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_psychologist_cannot_access_other_psychologist_followup(
        self,
    ):
        StudentProfessionalAssignment.objects.create(
            student=self.assigned_student,
            professional=self.other_psychologist,
            professional_role="PSICOLOGO",
            assigned_by=self.responsible,
            is_active=True,
        )

        other_followup = (
            PsychologicalFollowUp.objects.create(
                student=self.assigned_student,
                followup_date=date(2026, 2, 5),
                reason="Seguimiento de otro profesional",
                observations=(
                    "Información psicológica confidencial."
                ),
                created_by=self.other_psychologist,
                updated_by=self.other_psychologist,
            )
        )

        self.authenticate(self.psychologist)

        list_response = self.client.get(
            self.psychological_context_url()
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in list_response.data
        }

        self.assertIn(
            self.assigned_followup.id,
            returned_ids,
        )
        self.assertNotIn(
            other_followup.id,
            returned_ids,
        )

        detail_url = reverse(
            "psychological-followup-detail",
            kwargs={
                "pk": other_followup.pk,
            },
        )

        detail_response = self.client.get(
            f"{detail_url}?context=PSICOLOGO"
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        patch_response = self.client.patch(
            f"{detail_url}?context=PSICOLOGO",
            {
                "observations": (
                    "Intento de modificación no autorizado."
                ),
            },
            format="json",
        )

        self.assertEqual(
            patch_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
