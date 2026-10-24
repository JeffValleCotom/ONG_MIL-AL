from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentAssignmentAPITests(APITestCase):

    def setUp(self):
        self.list_url = reverse(
            "student-assignment-list"
        )
        self.eligible_url = reverse(
            "student-assignment-eligible-professionals"
        )

        self.responsible = self.create_user_with_role(
            username="responsable_asignaciones",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.docente = self.create_user_with_role(
            username="docente_asignable",
            role_name="DOCENTE",
        )

        self.psicologo = self.create_user_with_role(
            username="psicologo_asignable",
            role_name="PSICOLOGO",
        )

        self.terapeuta = self.create_user_with_role(
            username="terapeuta_asignable",
            role_name="TERAPEUTA",
        )

        self.student = Student.objects.create(
            institutional_code="MIL-ASG-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2024-01-15",
            is_active=True,
        )

    def create_user_with_role(
        self,
        username,
        role_name,
        is_active=True,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalAssignments123!",
            is_active=is_active,
        )

        user.groups.add(
            Group.objects.get(
                name=role_name,
            )
        )

        return user

    def authenticate_responsible(self):
        self.client.force_authenticate(
            user=self.responsible
        )

    def create_assignment(
        self,
        professional=None,
        professional_role="DOCENTE",
    ):
        if professional is None:
            professional = self.docente

        return StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role=professional_role,
            assigned_by=self.responsible,
        )

    def test_responsible_can_list_assignments(self):
        assignment = self.create_assignment()

        self.authenticate_responsible()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            assignment.id,
        )

    def test_responsible_can_get_eligible_professionals_by_role(
        self,
    ):
        self.authenticate_responsible()

        response = self.client.get(
            self.eligible_url,
            {
                "role": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            professional["id"]
            for professional in response.data
        }

        self.assertIn(
            self.docente.id,
            returned_ids,
        )

        self.assertNotIn(
            self.psicologo.id,
            returned_ids,
        )

        self.assertNotIn(
            self.terapeuta.id,
            returned_ids,
        )

    def test_eligible_professionals_excludes_inactive_users(
        self,
    ):
        inactive_docente = self.create_user_with_role(
            username="docente_inactivo",
            role_name="DOCENTE",
            is_active=False,
        )

        self.authenticate_responsible()

        response = self.client.get(
            self.eligible_url,
            {
                "role": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            professional["id"]
            for professional in response.data
        }

        self.assertNotIn(
            inactive_docente.id,
            returned_ids,
        )

    def test_eligible_professionals_requires_valid_role(
        self,
    ):
        self.authenticate_responsible()

        missing_role_response = self.client.get(
            self.eligible_url
        )

        self.assertEqual(
            missing_role_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        invalid_role_response = self.client.get(
            self.eligible_url,
            {
                "role": "ADMINISTRADOR",
            },
        )

        self.assertEqual(
            invalid_role_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_responsible_can_create_assignment(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.docente.id,
                "professional_role": "DOCENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        assignment = (
            StudentProfessionalAssignment.objects.get()
        )

        self.assertEqual(
            assignment.student,
            self.student,
        )

        self.assertEqual(
            assignment.professional,
            self.docente,
        )

        self.assertEqual(
            assignment.professional_role,
            "DOCENTE",
        )

        self.assertEqual(
            assignment.assigned_by,
            self.responsible,
        )

        self.assertTrue(
            assignment.is_active
        )

        self.assertIsNone(
            assignment.unassigned_at
        )

    def test_client_cannot_override_assignment_metadata(
        self,
    ):
        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.docente.id,
                "professional_role": "DOCENTE",
                "is_active": False,
                "assigned_by": self.docente.id,
                "unassigned_at": "2026-01-01T12:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        assignment = (
            StudentProfessionalAssignment.objects.get()
        )

        self.assertTrue(
            assignment.is_active
        )

        self.assertEqual(
            assignment.assigned_by,
            self.responsible,
        )

        self.assertIsNone(
            assignment.unassigned_at
        )

    def test_assignment_to_inactive_student_is_rejected(
        self,
    ):
        self.student.is_active = False
        self.student.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.docente.id,
                "professional_role": "DOCENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "student_id",
            response.data,
        )

        self.assertFalse(
            StudentProfessionalAssignment.objects.exists()
        )

    def test_assignment_to_inactive_professional_is_rejected(
        self,
    ):
        self.docente.is_active = False
        self.docente.save(
            update_fields=[
                "is_active",
            ]
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.docente.id,
                "professional_role": "DOCENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "professional_id",
            response.data,
        )

        self.assertFalse(
            StudentProfessionalAssignment.objects.exists()
        )

    def test_professional_must_have_requested_role(
        self,
    ):
        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.psicologo.id,
                "professional_role": "DOCENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "professional_id",
            response.data,
        )

        self.assertFalse(
            StudentProfessionalAssignment.objects.exists()
        )

    def test_duplicate_active_assignment_is_rejected(
        self,
    ):
        self.create_assignment()

        self.authenticate_responsible()

        response = self.client.post(
            self.list_url,
            {
                "student_id": self.student.id,
                "professional_id": self.docente.id,
                "professional_role": "DOCENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            StudentProfessionalAssignment.objects.count(),
            1,
        )

    def test_responsible_can_finish_assignment(self):
        assignment = self.create_assignment()

        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-assignment-finish",
                kwargs={
                    "pk": assignment.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()

        self.assertFalse(
            assignment.is_active
        )

        self.assertIsNotNone(
            assignment.unassigned_at
        )

    def test_finish_assignment_is_idempotent(self):
        assignment = self.create_assignment()

        self.authenticate_responsible()

        finish_url = reverse(
            "student-assignment-finish",
            kwargs={
                "pk": assignment.pk,
            },
        )

        first_response = self.client.patch(
            finish_url,
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()
        first_unassigned_at = assignment.unassigned_at

        second_response = self.client.patch(
            finish_url,
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        assignment.refresh_from_db()

        self.assertEqual(
            assignment.unassigned_at,
            first_unassigned_at,
        )

    def test_finished_assignment_is_preserved_as_history(
        self,
    ):
        assignment = self.create_assignment()

        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-assignment-finish",
                kwargs={
                    "pk": assignment.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            StudentProfessionalAssignment.objects.filter(
                pk=assignment.pk,
                is_active=False,
                unassigned_at__isnull=False,
            ).exists()
        )

    def test_delete_assignment_is_not_allowed(self):
        assignment = self.create_assignment()

        self.authenticate_responsible()

        response = self.client.delete(
            reverse(
                "student-assignment-detail",
                kwargs={
                    "pk": assignment.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            StudentProfessionalAssignment.objects.filter(
                pk=assignment.pk,
            ).exists()
        )

    def test_professional_roles_cannot_manage_assignments(
        self,
    ):
        for role_name in (
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
        ):
            with self.subTest(role=role_name):
                operator = self.create_user_with_role(
                    username=(
                        f"assignment_{role_name.lower()}"
                    ),
                    role_name=role_name,
                )

                self.client.force_authenticate(
                    user=operator
                )

                response = self.client.get(
                    self.list_url
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_administrator_cannot_manage_assignments(
        self,
    ):
        administrator = self.create_user_with_role(
            username="assignment_administrator",
            role_name="ADMINISTRADOR",
        )

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superuser_does_not_bypass_assignment_permission(
        self,
    ):
        superuser = User.objects.create_superuser(
            username="assignment_superuser",
            email="assignment-superuser@test.com",
            password="MilalSuper123!",
        )

        self.client.force_authenticate(
            user=superuser
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonymous_user_cannot_manage_assignments(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )