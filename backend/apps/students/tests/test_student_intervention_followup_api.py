from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentInterventionFollowUp,
    StudentInterventionPlan,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentInterventionFollowUpAPITests(APITestCase):
    def setUp(self):
        self.psychology_group = Group.objects.get(
            name="PSICOLOGO",
        )
        self.therapy_group = Group.objects.get(
            name="TERAPEUTA",
        )

        self.psychologist = self.create_user(
            "followup_psychologist",
            self.psychology_group,
        )

        self.other_psychologist = self.create_user(
            "followup_other_psychologist",
            self.psychology_group,
        )

        self.therapist = self.create_user(
            "followup_therapist",
            self.therapy_group,
        )

        self.assigner = User.objects.create_user(
            username="followup_assigner",
            password="test-password",
        )

        self.student = Student.objects.create(
            institutional_code="FOLLOW-001",
            first_name="Estudiante",
            last_name="Seguimiento",
            date_of_birth="2014-05-10",
            admission_date="2025-01-15",
        )

        self.assign_student(
            self.psychologist,
            "PSICOLOGO",
        )

        self.assign_student(
            self.other_psychologist,
            "PSICOLOGO",
        )

        self.assign_student(
            self.therapist,
            "TERAPEUTA",
        )

        self.plan = self.create_plan()

    def create_user(
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
        professional,
        role,
    ):
        return StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role=role,
            assigned_by=self.assigner,
        )

    def create_plan(
        self,
        *,
        creator=None,
        creator_role="PSICOLOGO",
        responsible=None,
        responsible_role="PSICOLOGO",
        plan_status="PLANNED",
    ):
        creator = creator or self.psychologist
        responsible = (
            responsible
            or self.psychologist
        )

        return StudentInterventionPlan.objects.create(
            student=self.student,
            objectives=(
                "Fortalecer habilidades de autorregulación."
            ),
            estimated_start_date=(
                timezone.localdate()
                + timedelta(days=7)
            ),
            estimated_end_date=(
                timezone.localdate()
                + timedelta(days=21)
            ),
            professional_role=creator_role,
            responsible=responsible,
            responsible_role=responsible_role,
            status=plan_status,
            created_by=creator,
            updated_by=creator,
        )

    def followup_url(
        self,
        plan=None,
        context="PSICOLOGO",
    ):
        plan = plan or self.plan

        return (
            reverse(
                "student-intervention-followups",
                kwargs={
                    "pk": self.student.pk,
                    "plan_id": plan.pk,
                },
            )
            + f"?context={context}"
        )

    def record_url(
        self,
        context="PSICOLOGO",
    ):
        return (
            reverse(
                "student-record",
                kwargs={
                    "pk": self.student.pk,
                },
            )
            + f"?context={context}"
        )

    def payload(
        self,
        *,
        plan_status="IN_PROGRESS",
        followup_date=None,
    ):
        return {
            "followup_date": str(
                followup_date
                or timezone.localdate()
            ),
            "progress": (
                "El estudiante muestra mayor participación."
            ),
            "results": (
                "Se observa avance parcial respecto "
                "al objetivo planteado."
            ),
            "observations": (
                "Continuar reforzando estrategias "
                "de autorregulación."
            ),
            "status": plan_status,
        }

    def test_psychologist_can_register_followup(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        followup = (
            StudentInterventionFollowUp.objects.get(
                pk=response.data["id"],
            )
        )

        self.assertEqual(
            followup.intervention_plan,
            self.plan,
        )

        self.assertEqual(
            followup.created_by,
            self.psychologist,
        )

    def test_followup_stores_progress_results_and_observations(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        followup = (
            StudentInterventionFollowUp.objects.get(
                pk=response.data["id"],
            )
        )

        self.assertIn(
            "mayor participación",
            followup.progress,
        )

        self.assertIn(
            "avance parcial",
            followup.results,
        )

        self.assertIn(
            "autorregulación",
            followup.observations,
        )

    def test_followup_updates_plan_status(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(
                plan_status="IN_PROGRESS",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.plan.refresh_from_db()

        self.assertEqual(
            self.plan.status,
            "IN_PROGRESS",
        )

    def test_invalid_status_transition_is_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(
                plan_status="COMPLETED",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            StudentInterventionFollowUp.objects.exists()
        )

        self.plan.refresh_from_db()

        self.assertEqual(
            self.plan.status,
            "PLANNED",
        )

    def test_future_followup_date_is_rejected(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(
                followup_date=(
                    timezone.localdate()
                    + timedelta(days=1)
                ),
            ),
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

    def test_multiple_followups_are_preserved_in_history(
        self,
    ):
        self.plan.status = "IN_PROGRESS"
        self.plan.save(
            update_fields=["status"],
        )

        StudentInterventionFollowUp.objects.create(
            intervention_plan=self.plan,
            followup_date=(
                timezone.localdate()
                - timedelta(days=7)
            ),
            progress="Primer avance.",
            results="Primer resultado.",
            observations="Primera observación.",
            status="IN_PROGRESS",
            created_by=self.psychologist,
        )

        StudentInterventionFollowUp.objects.create(
            intervention_plan=self.plan,
            followup_date=timezone.localdate(),
            progress="Segundo avance.",
            results="Segundo resultado.",
            observations="Segunda observación.",
            status="IN_PROGRESS",
            created_by=self.psychologist,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.get(
            self.record_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        plans = (
            response.data["sections"]
            ["interventions"]["planned"]
        )

        plan_data = next(
            item
            for item in plans
            if item["id"] == self.plan.id
        )

        self.assertEqual(
            len(plan_data["followups"]),
            2,
        )

    def test_responsible_can_register_followup(
        self,
    ):
        plan = self.create_plan(
            creator=self.therapist,
            creator_role="TERAPEUTA",
            responsible=self.psychologist,
            responsible_role="PSICOLOGO",
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(plan),
            self.payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_unrelated_professional_cannot_register_followup(
        self,
    ):
        self.client.force_authenticate(
            user=self.other_psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            StudentInterventionFollowUp.objects.exists()
        )

    def test_completed_plan_rejects_new_followups(
        self,
    ):
        self.plan.status = "COMPLETED"
        self.plan.save(
            update_fields=["status"],
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(
                plan_status="COMPLETED",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            StudentInterventionFollowUp.objects.exists()
        )

    def test_cancelled_plan_rejects_new_followups(
        self,
    ):
        self.plan.status = "CANCELLED"
        self.plan.save(
            update_fields=["status"],
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.followup_url(),
            self.payload(
                plan_status="CANCELLED",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            StudentInterventionFollowUp.objects.exists()
        )
