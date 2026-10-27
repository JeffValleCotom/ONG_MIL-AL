from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import AcademicFollowUp
from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)


User = get_user_model()


class AcademicFollowUpAPITests(APITestCase):
    def setUp(self):
        self.student_ana = Student.objects.create(
            institutional_code="MIL-ACA-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2024-01-15",
            is_active=True,
        )

        self.student_carlos = Student.objects.create(
            institutional_code="MIL-ACA-002",
            first_name="Carlos",
            last_name="Pérez",
            date_of_birth="2014-08-20",
            admission_date="2023-02-01",
            is_active=True,
        )

        self.student_inactive = Student.objects.create(
            institutional_code="MIL-ACA-003",
            first_name="María",
            last_name="Gómez",
            date_of_birth="2016-03-12",
            admission_date="2025-01-10",
            is_active=False,
        )

        self.assignment_manager = (
            self.create_user_with_role(
                username="responsable_academic_fixture",
                role_name="RESPONSABLE_INSTITUCIONAL",
            )
        )

        self.list_url = reverse(
            "academic-followup-list"
        )

    def create_user_with_role(
        self,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalAcademic123!",
        )

        user.groups.add(
            Group.objects.get(name=role_name)
        )

        return user

    def assign_student(
        self,
        professional,
        student,
        professional_role="DOCENTE",
    ):
        return StudentProfessionalAssignment.objects.create(
            student=student,
            professional=professional,
            professional_role=professional_role,
            assigned_by=self.assignment_manager,
        )

    def create_followup(
        self,
        student,
        author,
        subject="Matemática",
    ):
        return AcademicFollowUp.objects.create(
            student=student,
            followup_date=timezone.localdate(),
            academic_period="2026 - Ciclo 2",
            subject=subject,
            observations=(
                "Seguimiento académico de prueba."
            ),
            strengths="Participación constante.",
            areas_for_improvement=(
                "Reforzar resolución de problemas."
            ),
            recommendations=(
                "Realizar ejercicios guiados."
            ),
            created_by=author,
            updated_by=author,
        )

    def valid_payload(self, student):
        return {
            "student_id": student.id,
            "followup_date": (
                timezone.localdate().isoformat()
            ),
            "academic_period": "2026 - Ciclo 2",
            "subject": "Matemática",
            "observations": (
                "Presenta avances en razonamiento lógico."
            ),
            "strengths": (
                "Mantiene buena participación."
            ),
            "areas_for_improvement": (
                "Debe reforzar operaciones básicas."
            ),
            "recommendations": (
                "Continuar con ejercicios prácticos."
            ),
        }

    def test_assigned_docente_can_list_followups(self):
        docente = self.create_user_with_role(
            username="docente_academic_list",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        followup = self.create_followup(
            student=self.student_ana,
            author=docente,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.list_url,
            {
                "context": "DOCENTE",
            },
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
            followup.id,
        )

    def test_docente_only_lists_assigned_students_followups(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_scope",
            role_name="DOCENTE",
        )

        other_docente = self.create_user_with_role(
            username="other_docente_academic",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        self.assign_student(
            professional=other_docente,
            student=self.student_carlos,
        )

        own_followup = self.create_followup(
            student=self.student_ana,
            author=docente,
            subject="Lenguaje",
        )

        self.create_followup(
            student=self.student_carlos,
            author=other_docente,
            subject="Ciencias",
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.list_url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            [
                item["id"]
                for item in response.data
            ],
            [
                own_followup.id,
            ],
        )

    def test_docente_cannot_retrieve_unassigned_followup(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_unassigned",
            role_name="DOCENTE",
        )

        other_docente = self.create_user_with_role(
            username="other_docente_detail",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        self.assign_student(
            professional=other_docente,
            student=self.student_carlos,
        )

        followup = self.create_followup(
            student=self.student_carlos,
            author=other_docente,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            reverse(
                "academic-followup-detail",
                kwargs={
                    "pk": followup.pk,
                },
            ),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_docente_can_create_followup_for_assigned_student(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_create",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.list_url}"
                "?context=DOCENTE"
            ),
            self.valid_payload(
                self.student_ana
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        followup = AcademicFollowUp.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            followup.student_id,
            self.student_ana.id,
        )

        self.assertEqual(
            followup.created_by,
            docente,
        )

        self.assertEqual(
            followup.updated_by,
            docente,
        )

    def test_docente_cannot_create_for_unassigned_student(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_create_attack",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.list_url}"
                "?context=DOCENTE"
            ),
            self.valid_payload(
                self.student_carlos
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            AcademicFollowUp.objects.filter(
                student=self.student_carlos,
            ).exists()
        )

    def test_cannot_create_followup_for_inactive_student(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_inactive",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_inactive,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.list_url}"
                "?context=DOCENTE"
            ),
            self.valid_payload(
                self.student_inactive
            ),
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

    def test_future_followup_date_is_rejected(self):
        docente = self.create_user_with_role(
            username="docente_academic_future",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        payload = self.valid_payload(
            self.student_ana
        )

        payload["followup_date"] = (
            timezone.localdate()
            + timedelta(days=1)
        ).isoformat()

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.list_url}"
                "?context=DOCENTE"
            ),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "followup_date",
            response.data,
        )

    def test_missing_context_is_rejected(self):
        docente = self.create_user_with_role(
            username="docente_academic_no_context",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "context",
            response.data,
        )

    def test_multi_role_user_cannot_use_academic_api_in_psychology_context(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_academic_context",
            password="MilalAcademic123!",
        )

        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
        )

        self.assign_student(
            professional=professional,
            student=self.student_ana,
            professional_role="DOCENTE",
        )

        self.client.force_authenticate(
            user=professional
        )

        response = self.client.get(
            self.list_url,
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_responsible_cannot_access_academic_api(self):
        responsible = self.create_user_with_role(
            username="responsable_academic_attack",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.client.force_authenticate(
            user=responsible
        )

        response = self.client.get(
            self.list_url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_docente_can_update_assigned_followup(self):
        docente = self.create_user_with_role(
            username="docente_academic_update",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        followup = self.create_followup(
            student=self.student_ana,
            author=docente,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.patch(
            (
                reverse(
                    "academic-followup-detail",
                    kwargs={
                        "pk": followup.pk,
                    },
                )
                + "?context=DOCENTE"
            ),
            {
                "observations": (
                    "Seguimiento académico actualizado."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        followup.refresh_from_db()

        self.assertEqual(
            followup.observations,
            "Seguimiento académico actualizado.",
        )

        self.assertEqual(
            followup.updated_by,
            docente,
        )

    def test_student_cannot_be_changed_during_update(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_academic_change_student",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        followup = self.create_followup(
            student=self.student_ana,
            author=docente,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.patch(
            (
                reverse(
                    "academic-followup-detail",
                    kwargs={
                        "pk": followup.pk,
                    },
                )
                + "?context=DOCENTE"
            ),
            {
                "student_id": self.student_carlos.id,
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

        followup.refresh_from_db()

        self.assertEqual(
            followup.student_id,
            self.student_ana.id,
        )

    def test_delete_is_not_allowed(self):
        docente = self.create_user_with_role(
            username="docente_academic_delete",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            student=self.student_ana,
        )

        followup = self.create_followup(
            student=self.student_ana,
            author=docente,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.delete(
            (
                reverse(
                    "academic-followup-detail",
                    kwargs={
                        "pk": followup.pk,
                    },
                )
                + "?context=DOCENTE"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            AcademicFollowUp.objects.filter(
                pk=followup.pk,
            ).exists()
        )

    def test_docente_cannot_access_other_docente_followup(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_owner",
            role_name="DOCENTE",
        )

        other_docente = self.create_user_with_role(
            username="docente_other_owner",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.assign_student(
            professional=other_docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        own_followup = self.create_followup(
            student=self.student_ana,
            author=docente,
        )

        other_followup = self.create_followup(
            student=self.student_ana,
            author=other_docente,
        )

        self.client.force_authenticate(
            user=docente,
        )

        list_response = self.client.get(
            self.list_url,
            {
                "context": "DOCENTE",
                "student": self.student_ana.id,
            },
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
            own_followup.id,
            returned_ids,
        )
        self.assertNotIn(
            other_followup.id,
            returned_ids,
        )

        detail_url = reverse(
            "academic-followup-detail",
            kwargs={
                "pk": other_followup.pk,
            },
        )

        detail_response = self.client.get(
            f"{detail_url}?context=DOCENTE"
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        patch_response = self.client.patch(
            f"{detail_url}?context=DOCENTE",
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
