from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)
from apps.therapy.models import TherapyFollowUp
from django.utils import timezone


User = get_user_model()


class DashboardAPITests(APITestCase):
    def setUp(self):
        self.url = reverse(
            "dashboard-overview"
        )

        self.docente = User.objects.create_user(
            username="dashboard_docente",
            password="test-password-123",
        )

        self.other_docente = User.objects.create_user(
            username="dashboard_other_docente",
            password="test-password-123",
        )

        self.responsable = User.objects.create_user(
            username="dashboard_responsable",
            password="test-password-123",
        )

        self.docente_group = Group.objects.get_or_create(
            name="DOCENTE",
        )[0]

        self.psicologo_group = Group.objects.get_or_create(
            name="PSICOLOGO",
        )[0]

        self.responsable_group = Group.objects.get_or_create(
            name="RESPONSABLE_INSTITUCIONAL",
        )[0]

        self.docente.groups.add(
            self.docente_group
        )

        self.other_docente.groups.add(
            self.docente_group
        )

        self.responsable.groups.add(
            self.responsable_group
        )

        dashboard_permission = Permission.objects.get(
            codename="view_dashboard",
            content_type__app_label="users",
        )

        self.docente.user_permissions.add(
            dashboard_permission
        )

        self.other_docente.user_permissions.add(
            dashboard_permission
        )

        self.responsable.user_permissions.add(
            dashboard_permission
        )

        self.assigned_student = self.create_student(
            "MIL-DASH-001",
            "Ana",
            "López",
        )

        self.other_student = self.create_student(
            "MIL-DASH-002",
            "Carlos",
            "Pérez",
        )

        self.inactive_student = self.create_student(
            "MIL-DASH-003",
            "Lucía",
            "Gómez",
            is_active=False,
        )

        self.create_assignment(
            student=self.assigned_student,
            professional=self.docente,
            role="DOCENTE",
        )

        self.create_assignment(
            student=self.other_student,
            professional=self.other_docente,
            role="DOCENTE",
        )

    def create_student(
        self,
        code,
        first_name,
        last_name,
        is_active=True,
    ):
        return Student.objects.create(
            institutional_code=code,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(2015, 1, 1),
            admission_date=date(2024, 1, 15),
            is_active=is_active,
        )

    def create_assignment(
        self,
        student,
        professional,
        role,
        is_active=True,
    ):
        assignment_data = {
            "student": student,
            "professional": professional,
            "professional_role": role,
            "is_active": is_active,
            "assigned_by": self.responsable,
        }

        if not is_active:
            assignment_data["unassigned_at"] = timezone.now()

        return StudentProfessionalAssignment.objects.create(
            **assignment_data
        )

    def authenticate(self, user):
        self.client.force_authenticate(
            user=user
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertIn(
            response.status_code,
            (
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ),
        )

    def test_dashboard_requires_view_dashboard_permission(self):
        dashboard_permission = Permission.objects.get(
            codename="view_dashboard",
            content_type__app_label="users",
        )

        self.docente_group.permissions.remove(
            dashboard_permission
        )

        user = User.objects.create_user(
            username="without_dashboard_permission",
            password="test-password-123",
        )

        user.groups.add(
            self.docente_group
        )

        self.authenticate(user)

        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_docente_only_sees_actively_assigned_students(self):
        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
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

        self.assertEqual(
            response.data["students"]["total"],
            1,
        )

        self.assertEqual(
            response.data["students"]["active"],
            1,
        )

        self.assertEqual(
            response.data["students"]["inactive"],
            0,
        )

        self.assertEqual(
            response.data["visible_areas"],
            (
                "academic",
                "evaluations",
            ),
        )

    def test_inactive_assignment_does_not_grant_student_scope(self):
        student = self.create_student(
            "MIL-DASH-004",
            "Diego",
            "Ramírez",
        )

        self.create_assignment(
            student=student,
            professional=self.docente,
            role="DOCENTE",
            is_active=False,
        )

        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["students"]["total"],
            1,
        )

    def test_period_filters_activity_but_not_student_summary(self):
        AcademicFollowUp.objects.create(
            student=self.assigned_student,
            followup_date=date(2026, 2, 10),
            academic_period="2026-1",
            subject="Matemática",
            observations="Seguimiento febrero.",
            created_by=self.docente,
            updated_by=self.docente,
        )

        AcademicFollowUp.objects.create(
            student=self.assigned_student,
            followup_date=date(2026, 9, 10),
            academic_period="2026-2",
            subject="Matemática",
            observations="Seguimiento septiembre.",
            created_by=self.docente,
            updated_by=self.docente,
        )

        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
                "date_from": "2026-01-01",
                "date_to": "2026-06-30",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["students"]["total"],
            1,
        )

        self.assertEqual(
            response.data[
                "activity"
            ]["indicators"]["academic"],
            1,
        )

        self.assertEqual(
            response.data["timeline"],
            [
                {
                    "period": "2026-02",
                    "academic": 1,
                    "evaluations": 0,
                }
            ],
        )

    def test_dashboard_uses_real_followup_and_evaluation_records(self):
        AcademicFollowUp.objects.create(
            student=self.assigned_student,
            followup_date=date(2026, 5, 10),
            academic_period="2026-1",
            subject="Lenguaje",
            observations="Seguimiento académico.",
            created_by=self.docente,
            updated_by=self.docente,
        )

        Evaluation.objects.create(
            student=self.assigned_student,
            evaluation_date=date(2026, 5, 20),
            evaluation_type="Evaluación de progreso",
            results="Resultados registrados.",
            professional_role="DOCENTE",
            created_by=self.docente,
            updated_by=self.docente,
        )

        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        indicators = response.data[
            "activity"
        ]["indicators"]

        self.assertEqual(
            indicators["academic"],
            1,
        )

        self.assertEqual(
            indicators["evaluations"],
            1,
        )

        self.assertEqual(
            response.data[
                "activity"
            ]["total_records"],
            2,
        )

    def test_multirole_user_must_send_context(self):
        self.docente.groups.add(
            self.psicologo_group
        )

        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "context",
            response.data,
        )

    def test_user_cannot_request_context_not_assigned(self):
        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_invalid_period_is_rejected(self):
        self.authenticate(
            self.docente
        )

        response = self.client.get(
            self.url,
            {
                "context": "DOCENTE",
                "date_from": "2026-12-31",
                "date_to": "2026-01-01",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "date_to",
            response.data,
        )

    def test_responsable_gets_general_dashboard(self):
        PsychologicalFollowUp.objects.create(
            student=self.other_student,
            followup_date=date(2026, 7, 10),
            reason="Seguimiento",
            observations="Registro psicológico.",
            created_by=self.responsable,
            updated_by=self.responsable,
        )

        TherapyFollowUp.objects.create(
            student=self.other_student,
            followup_date=date(2026, 7, 12),
            therapy_area="Lenguaje",
            objectives="Objetivos terapéuticos.",
            progress_notes="Avances registrados.",
            created_by=self.responsable,
            updated_by=self.responsable,
        )

        self.authenticate(
            self.responsable
        )

        response = self.client.get(
            self.url,
            {
                "context": (
                    "RESPONSABLE_INSTITUCIONAL"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["students"]["total"],
            3,
        )

        self.assertEqual(
            response.data["students"]["active"],
            2,
        )

        self.assertEqual(
            response.data["students"]["inactive"],
            1,
        )

        indicators = response.data[
            "activity"
        ]["indicators"]

        self.assertEqual(
            indicators["psychological"],
            1,
        )

        self.assertEqual(
            indicators["therapy"],
            1,
        )

        self.assertIn(
            "interventions",
            indicators,
        )
