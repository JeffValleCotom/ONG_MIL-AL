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


class StudentRecordAPITests(APITestCase):
    def setUp(self):
        self.student_ana = Student.objects.create(
            institutional_code="MIL-REC-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2024-01-15",
            is_active=True,
        )

        self.student_maria = Student.objects.create(
            institutional_code="MIL-REC-002",
            first_name="María",
            last_name="Pérez",
            date_of_birth="2016-03-12",
            admission_date="2025-01-10",
            is_active=True,
        )

        self.assignment_manager = self.create_user_with_role(
            username="responsable_record_fixture",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

    def create_user_with_role(
        self,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalRecord123!",
        )

        user.groups.add(
            Group.objects.get(name=role_name)
        )

        return user

    def assign_student(
        self,
        professional,
        professional_role,
        student,
    ):
        return StudentProfessionalAssignment.objects.create(
            student=student,
            professional=professional,
            professional_role=professional_role,
            assigned_by=self.assignment_manager,
        )

    def record_url(self, student):
        return reverse(
            "student-record",
            kwargs={
                "pk": student.pk,
            },
        )

    def test_responsible_can_retrieve_base_record(self):
        responsible = self.create_user_with_role(
            username="responsable_record",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.client.force_authenticate(
            user=responsible
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["student_id"],
            self.student_ana.id,
        )

        self.assertEqual(
            response.data["context"],
            "RESPONSABLE_INSTITUCIONAL",
        )

        general = response.data["sections"]["general"]

        self.assertEqual(
            general["institutional_code"],
            "MIL-REC-001",
        )
        self.assertEqual(
            general["first_name"],
            "Ana",
        )

    def test_assigned_docente_can_retrieve_record(self):
        docente = self.create_user_with_role(
            username="docente_record",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["context"],
            "DOCENTE",
        )

    def test_professional_cannot_retrieve_unassigned_record(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_unassigned",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.record_url(self.student_maria),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_record_only_contains_base_general_section(self):
        responsable = self.create_user_with_role(
            username="responsable_record_sections",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.client.force_authenticate(
            user=responsable
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            set(response.data["sections"].keys()),
            {
                "general",
            },
        )

        self.assertNotIn(
            "academic",
            response.data["sections"],
        )
        self.assertNotIn(
            "psychological",
            response.data["sections"],
        )
        self.assertNotIn(
            "therapy",
            response.data["sections"],
        )

    def test_multi_role_user_must_specify_record_context(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_record_context",
            password="MilalRecord123!",
        )

        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
        )

        self.client.force_authenticate(
            user=professional
        )

        response = self.client.get(
            self.record_url(self.student_ana)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "context",
            response.data,
        )

    def test_multi_role_record_contexts_remain_isolated(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_record_isolated",
            password="MilalRecord123!",
        )

        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
        )

        self.assign_student(
            professional=professional,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.assign_student(
            professional=professional,
            professional_role="PSICOLOGO",
            student=self.student_maria,
        )

        self.client.force_authenticate(
            user=professional
        )

        docente_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_200_OK,
        )

        psicologo_attack = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            psicologo_attack.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        psicologo_response = self.client.get(
            self.record_url(self.student_maria),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            psicologo_response.status_code,
            status.HTTP_200_OK,
        )

    def test_user_cannot_request_record_context_not_owned(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_attack",
            role_name="DOCENTE",
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_administrator_cannot_retrieve_record(self):
        administrator = self.create_user_with_role(
            username="admin_record",
            role_name="ADMINISTRADOR",
        )

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.get(
            self.record_url(self.student_ana)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonymous_user_cannot_retrieve_record(self):
        response = self.client.get(
            self.record_url(self.student_ana)
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )