from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentIntervention,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentInterventionAPITests(APITestCase):
    def setUp(self):
        self.psychology_group = Group.objects.get(
            name="PSICOLOGO",
        )
        self.therapy_group = Group.objects.get(
            name="TERAPEUTA",
        )
        self.teacher_group = Group.objects.get(
            name="DOCENTE",
        )

        self.psychologist = self.create_user_with_role(
            username="intervention_psychologist",
            group=self.psychology_group,
        )

        self.therapist = self.create_user_with_role(
            username="intervention_therapist",
            group=self.therapy_group,
        )

        self.other_psychologist = self.create_user_with_role(
            username="intervention_other_psychologist",
            group=self.psychology_group,
        )

        self.teacher = self.create_user_with_role(
            username="intervention_teacher",
            group=self.teacher_group,
        )

        self.assigner = User.objects.create_user(
            username="intervention_assigner",
            password="test-password",
        )

        self.student = Student.objects.create(
            institutional_code="INT-001",
            first_name="Estudiante",
            last_name="Intervencion",
            date_of_birth="2015-05-10",
            admission_date="2025-01-15",
        )

        self.inactive_student = Student.objects.create(
            institutional_code="INT-002",
            first_name="Estudiante",
            last_name="Inactivo",
            date_of_birth="2014-03-08",
            admission_date="2024-02-01",
            is_active=False,
        )

        self.assign_student(
            self.student,
            self.psychologist,
            "PSICOLOGO",
        )

        self.assign_student(
            self.student,
            self.therapist,
            "TERAPEUTA",
        )

        self.assign_student(
            self.student,
            self.other_psychologist,
            "PSICOLOGO",
        )

        self.assign_student(
            self.inactive_student,
            self.psychologist,
            "PSICOLOGO",
        )

    def create_user_with_role(
        self,
        username,
        group,
    ):
        user = User.objects.create_user(
            username=username,
            password="test-password",
        )
        user.groups.add(group)
        return user

    def assign_student(
        self,
        student,
        professional,
        professional_role,
    ):
        return StudentProfessionalAssignment.objects.create(
            student=student,
            professional=professional,
            professional_role=professional_role,
            assigned_by=self.assigner,
        )

    def interventions_url(
        self,
        student=None,
    ):
        student = student or self.student

        return reverse(
            "student-interventions",
            kwargs={
                "pk": student.pk,
            },
        )

    def intervention_detail_url(
        self,
        intervention,
    ):
        return reverse(
            "student-intervention-detail",
            kwargs={
                "pk": intervention.student_id,
                "intervention_id": intervention.pk,
            },
        )

    def create_intervention(
        self,
        *,
        student=None,
        professional=None,
        professional_role="PSICOLOGO",
        objectives="Fortalecer habilidades del estudiante.",
        observations="El estudiante participó adecuadamente.",
    ):
        student = student or self.student
        professional = professional or self.psychologist

        return StudentIntervention.objects.create(
            student=student,
            intervention_date=timezone.localdate(),
            professional_role=professional_role,
            objectives=objectives,
            observations=observations,
            created_by=professional,
            updated_by=professional,
        )

    def test_psychologist_can_register_intervention(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.interventions_url(),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": (
                    "Fortalecer regulación emocional."
                ),
                "observations": (
                    "Se trabajaron estrategias de autorregulación."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        intervention = StudentIntervention.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            intervention.student,
            self.student,
        )
        self.assertEqual(
            intervention.created_by,
            self.psychologist,
        )
        self.assertEqual(
            intervention.updated_by,
            self.psychologist,
        )
        self.assertEqual(
            intervention.professional_role,
            "PSICOLOGO",
        )
        self.assertEqual(
            response.data["responsible"]["id"],
            self.psychologist.id,
        )

    def test_therapist_can_register_intervention(self):
        self.client.force_authenticate(
            user=self.therapist,
        )

        response = self.client.post(
            self.interventions_url(),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": (
                    "Favorecer coordinación motora."
                ),
                "observations": (
                    "Se realizaron actividades terapéuticas."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        intervention = StudentIntervention.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            intervention.student,
            self.student,
        )
        self.assertEqual(
            intervention.created_by,
            self.therapist,
        )
        self.assertEqual(
            intervention.professional_role,
            "TERAPEUTA",
        )

    def test_psychologist_can_query_own_interventions(self):
        own_intervention = self.create_intervention()

        other_intervention = self.create_intervention(
            professional=self.other_psychologist,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.get(
            self.interventions_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        intervention_ids = {
            item["id"]
            for item in response.data["items"]
        }

        self.assertIn(
            own_intervention.id,
            intervention_ids,
        )
        self.assertNotIn(
            other_intervention.id,
            intervention_ids,
        )

    def test_psychologist_can_modify_own_intervention(self):
        intervention = self.create_intervention()

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.patch(
            self.intervention_detail_url(
                intervention
            ),
            {
                "objectives": (
                    "Objetivo actualizado."
                ),
                "observations": (
                    "Observación actualizada."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        intervention.refresh_from_db()

        self.assertEqual(
            intervention.objectives,
            "Objetivo actualizado.",
        )
        self.assertEqual(
            intervention.observations,
            "Observación actualizada.",
        )
        self.assertEqual(
            intervention.created_by,
            self.psychologist,
        )
        self.assertEqual(
            intervention.updated_by,
            self.psychologist,
        )

    def test_professional_cannot_modify_another_users_intervention(
        self,
    ):
        intervention = self.create_intervention(
            professional=self.other_psychologist,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.patch(
            self.intervention_detail_url(
                intervention
            ),
            {
                "observations": (
                    "Intento de modificación no autorizado."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_unassigned_professional_cannot_register_intervention(
        self,
    ):
        unassigned_student = Student.objects.create(
            institutional_code="INT-003",
            first_name="Sin",
            last_name="Asignacion",
            date_of_birth="2015-04-20",
            admission_date="2025-01-20",
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.interventions_url(
                unassigned_student
            ),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": "Objetivo de prueba.",
                "observations": "Observación de prueba.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            StudentIntervention.objects.filter(
                student=unassigned_student,
            ).exists()
        )

    def test_cannot_register_intervention_for_inactive_student(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.interventions_url(
                self.inactive_student
            ),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": "Objetivo de prueba.",
                "observations": "Observación de prueba.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_future_intervention_date_is_rejected(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        future_date = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.interventions_url(),
            {
                "intervention_date": str(
                    future_date
                ),
                "objectives": "Objetivo de prueba.",
                "observations": "Observación de prueba.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "intervention_date",
            response.data,
        )

    def test_blank_objectives_and_observations_are_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.interventions_url(),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": "",
                "observations": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "objectives",
            response.data,
        )
        self.assertIn(
            "observations",
            response.data,
        )

    def test_teacher_cannot_access_interventions(self):
        self.client.force_authenticate(
            user=self.teacher,
        )

        response = self.client.get(
            self.interventions_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_without_manage_permission_cannot_register(
        self,
    ):
        manage_permission = Permission.objects.get(
            codename="manage_interventions",
        )

        self.psychology_group.permissions.remove(
            manage_permission,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.interventions_url(),
            {
                "intervention_date": str(
                    timezone.localdate()
                ),
                "objectives": "Objetivo de prueba.",
                "observations": "Observación de prueba.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            StudentIntervention.objects.count(),
            0,
        )

    def test_user_without_view_permission_cannot_query(
        self,
    ):
        view_permission = Permission.objects.get(
            codename="view_interventions",
        )

        self.psychology_group.permissions.remove(
            view_permission,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.get(
            self.interventions_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
