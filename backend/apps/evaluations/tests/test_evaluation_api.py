from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    Group,
    Permission,
)
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)

from apps.evaluations.models import Evaluation


User = get_user_model()


class EvaluationAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.docente_group = Group.objects.get(
            name="DOCENTE",
        )
        cls.psychologist_group = Group.objects.get(
            name="PSICOLOGO",
        )
        cls.therapist_group = Group.objects.get(
            name="TERAPEUTA",
        )
        cls.responsible_group = Group.objects.get(
            name="RESPONSABLE_INSTITUCIONAL",
        )

        cls.responsible = User.objects.create_user(
            username="evaluation_responsible",
            password="test-password",
        )
        cls.responsible.groups.add(
            cls.responsible_group,
        )

        cls.therapist = User.objects.create_user(
            username="evaluation_therapist",
            password="test-password",
        )
        cls.therapist.groups.add(
            cls.therapist_group,
        )

        cls.other_therapist = User.objects.create_user(
            username="evaluation_other_therapist",
            password="test-password",
        )
        cls.other_therapist.groups.add(
            cls.therapist_group,
        )

        cls.multi_role_user = User.objects.create_user(
            username="evaluation_multi_role",
            password="test-password",
        )
        cls.multi_role_user.groups.add(
            cls.psychologist_group,
            cls.therapist_group,
        )

        cls.assigned_student = Student.objects.create(
            institutional_code="MIL-EV-001",
            first_name="Ana",
            last_name="Evaluacion",
            date_of_birth=date(2012, 4, 10),
            admission_date=date(2025, 4, 10),
            is_active=True,
        )

        cls.unassigned_student = Student.objects.create(
            institutional_code="MIL-EV-002",
            first_name="Mario",
            last_name="NoAsignado",
            date_of_birth=date(2013, 5, 10),
            admission_date=date(2025, 5, 10),
            is_active=True,
        )

        cls.inactive_student = Student.objects.create(
            institutional_code="MIL-EV-003",
            first_name="Sofia",
            last_name="Inactiva",
            date_of_birth=date(2011, 6, 10),
            admission_date=date(2025, 6, 10),
            is_active=False,
        )

        cls.therapist_assignment = (
            StudentProfessionalAssignment.objects.create(
                student=cls.assigned_student,
                professional=cls.therapist,
                professional_role="TERAPEUTA",
                assigned_by=cls.responsible,
                is_active=True,
            )
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

        cls.assigned_evaluation = Evaluation.objects.create(
            student=cls.assigned_student,
            evaluation_date=date(2026, 1, 15),
            evaluation_type="Evaluacion funcional",
            results="Resultados iniciales.",
            observations="Observaciones iniciales.",
            professional_role="TERAPEUTA",
            created_by=cls.therapist,
            updated_by=cls.therapist,
        )

        cls.historical_evaluation = (
            Evaluation.objects.create(
                student=cls.assigned_student,
                evaluation_date=date(2025, 12, 10),
                evaluation_type="Evaluacion previa",
                results="Resultado historico.",
                observations="Registro previo.",
                professional_role="TERAPEUTA",
                created_by=cls.other_therapist,
                updated_by=cls.other_therapist,
            )
        )

        cls.unassigned_evaluation = (
            Evaluation.objects.create(
                student=cls.unassigned_student,
                evaluation_date=date(2026, 1, 16),
                evaluation_type="Evaluacion no asignada",
                results="No debe ser visible.",
                professional_role="TERAPEUTA",
                created_by=cls.other_therapist,
                updated_by=cls.other_therapist,
            )
        )

        cls.multi_therapy_evaluation = (
            Evaluation.objects.create(
                student=cls.assigned_student,
                evaluation_date=date(2026, 2, 1),
                evaluation_type="Evaluacion terapeutica",
                results="Resultado terapeutico.",
                professional_role="TERAPEUTA",
                created_by=cls.multi_role_user,
                updated_by=cls.multi_role_user,
            )
        )

        cls.multi_psychological_evaluation = (
            Evaluation.objects.create(
                student=cls.assigned_student,
                evaluation_date=date(2026, 2, 2),
                evaluation_type="Evaluacion psicologica",
                results="Resultado psicologico.",
                professional_role="PSICOLOGO",
                created_by=cls.multi_role_user,
                updated_by=cls.multi_role_user,
            )
        )

    def authenticate(self, user):
        self.client.force_authenticate(
            user=user,
        )

    def evaluation_list_url(
        self,
        context,
        student=None,
    ):
        url = (
            f"{reverse('evaluation-list')}"
            f"?context={context}"
        )

        if student is not None:
            url += f"&student={student.pk}"

        return url

    def evaluation_detail_url(
        self,
        evaluation,
        context="TERAPEUTA",
    ):
        return (
            reverse(
                "evaluation-detail",
                kwargs={
                    "pk": evaluation.pk,
                },
            )
            + f"?context={context}"
        )

    def test_create_derives_role_and_audit_from_context(
        self,
    ):
        self.authenticate(self.therapist)

        response = self.client.post(
            self.evaluation_list_url("TERAPEUTA"),
            {
                "student_id": self.assigned_student.id,
                "evaluation_date": "2026-03-10",
                "evaluation_type": "Motricidad fina",
                "results": "Evolucion favorable.",
                "observations": "Continuar seguimiento.",
                "professional_role": "PSICOLOGO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        evaluation = Evaluation.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            evaluation.professional_role,
            "TERAPEUTA",
        )
        self.assertEqual(
            evaluation.created_by,
            self.therapist,
        )
        self.assertEqual(
            evaluation.updated_by,
            self.therapist,
        )
        self.assertEqual(
            evaluation.student,
            self.assigned_student,
        )

    def test_create_rejects_unassigned_and_inactive_students(
        self,
    ):
        self.authenticate(self.therapist)

        payload = {
            "evaluation_date": "2026-03-10",
            "evaluation_type": "Evaluacion funcional",
            "results": "Resultado.",
            "observations": "",
        }

        unassigned_response = self.client.post(
            self.evaluation_list_url("TERAPEUTA"),
            {
                **payload,
                "student_id": self.unassigned_student.id,
            },
            format="json",
        )

        self.assertEqual(
            unassigned_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        inactive_response = self.client.post(
            self.evaluation_list_url("TERAPEUTA"),
            {
                **payload,
                "student_id": self.inactive_student.id,
            },
            format="json",
        )

        self.assertEqual(
            inactive_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_rejects_future_evaluation_date(
        self,
    ):
        self.authenticate(self.therapist)

        future_date = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.evaluation_list_url("TERAPEUTA"),
            {
                "student_id": self.assigned_student.id,
                "evaluation_date": future_date.isoformat(),
                "evaluation_type": "Evaluacion futura",
                "results": "Resultado.",
                "observations": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "evaluation_date",
            response.data,
        )

    def test_list_includes_same_context_history_only_for_assigned_students(
        self,
    ):
        self.authenticate(self.therapist)

        response = self.client.get(
            self.evaluation_list_url(
                "TERAPEUTA",
                self.assigned_student,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        evaluation_ids = {
            item["id"]
            for item in response.data
        }

        self.assertIn(
            self.assigned_evaluation.id,
            evaluation_ids,
        )
        self.assertIn(
            self.historical_evaluation.id,
            evaluation_ids,
        )
        self.assertNotIn(
            self.unassigned_evaluation.id,
            evaluation_ids,
        )

        self.assertTrue(
            all(
                item["professional_role"] == "TERAPEUTA"
                for item in response.data
            )
        )

    def test_multi_role_user_is_isolated_by_current_context(
        self,
    ):
        self.authenticate(self.multi_role_user)

        therapy_response = self.client.get(
            self.evaluation_list_url(
                "TERAPEUTA",
                self.assigned_student,
            )
        )

        psychology_response = self.client.get(
            self.evaluation_list_url(
                "PSICOLOGO",
                self.assigned_student,
            )
        )

        self.assertEqual(
            therapy_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            psychology_response.status_code,
            status.HTTP_200_OK,
        )

        therapy_ids = {
            item["id"]
            for item in therapy_response.data
        }

        psychology_ids = {
            item["id"]
            for item in psychology_response.data
        }

        self.assertIn(
            self.multi_therapy_evaluation.id,
            therapy_ids,
        )
        self.assertNotIn(
            self.multi_psychological_evaluation.id,
            therapy_ids,
        )

        self.assertIn(
            self.multi_psychological_evaluation.id,
            psychology_ids,
        )
        self.assertNotIn(
            self.multi_therapy_evaluation.id,
            psychology_ids,
        )

    def test_view_permission_does_not_grant_management(
        self,
    ):
        manage_permission = Permission.objects.get(
            content_type__app_label="users",
            content_type__model="user",
            codename="manage_evaluations",
        )

        self.therapist_group.permissions.remove(
            manage_permission,
        )

        self.authenticate(self.therapist)

        list_response = self.client.get(
            self.evaluation_list_url("TERAPEUTA")
        )

        create_response = self.client.post(
            self.evaluation_list_url("TERAPEUTA"),
            {
                "student_id": self.assigned_student.id,
                "evaluation_date": "2026-03-10",
                "evaluation_type": "Sin permiso",
                "results": "No debe registrarse.",
            },
            format="json",
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            create_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_partial_update_preserves_student_and_context(
        self,
    ):
        self.authenticate(self.therapist)

        url = self.evaluation_detail_url(
            self.assigned_evaluation,
        )

        update_response = self.client.patch(
            url,
            {
                "results": "Resultado actualizado.",
                "observations": "Observacion actualizada.",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_evaluation.refresh_from_db()

        self.assertEqual(
            self.assigned_evaluation.results,
            "Resultado actualizado.",
        )
        self.assertEqual(
            self.assigned_evaluation.updated_by,
            self.therapist,
        )

        student_response = self.client.patch(
            url,
            {
                "student_id": self.unassigned_student.id,
            },
            format="json",
        )

        self.assertEqual(
            student_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        role_response = self.client.patch(
            url,
            {
                "professional_role": "PSICOLOGO",
            },
            format="json",
        )

        self.assertEqual(
            role_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assigned_evaluation.refresh_from_db()

        self.assertEqual(
            self.assigned_evaluation.student,
            self.assigned_student,
        )
        self.assertEqual(
            self.assigned_evaluation.professional_role,
            "TERAPEUTA",
        )

    def test_delete_is_not_allowed(self):
        self.authenticate(self.therapist)

        response = self.client.delete(
            self.evaluation_detail_url(
                self.assigned_evaluation,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            Evaluation.objects.filter(
                pk=self.assigned_evaluation.pk,
            ).exists()
        )

    def test_assignment_revocation_removes_access(
        self,
    ):
        self.authenticate(self.therapist)

        assignment = (
            StudentProfessionalAssignment.objects.get(
                student=self.assigned_student,
                professional=self.therapist,
                professional_role="TERAPEUTA",
                is_active=True,
            )
        )

        assignment.is_active = False
        assignment.unassigned_at = timezone.now()
        assignment.save(
            update_fields=[
                "is_active",
                "unassigned_at",
                "updated_at",
            ]
        )

        response = self.client.get(
            self.evaluation_detail_url(
                self.assigned_evaluation,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_borrow_another_professional_context(
        self,
    ):
        self.authenticate(self.therapist)

        response = self.client.get(
            self.evaluation_list_url("PSICOLOGO")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
