from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentInterventionPlan,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentInterventionPlanningAPITests(APITestCase):
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
            "planning_psychologist",
            self.psychology_group,
        )

        self.other_psychologist = (
            self.create_user_with_role(
                "planning_other_psychologist",
                self.psychology_group,
            )
        )

        self.therapist = self.create_user_with_role(
            "planning_therapist",
            self.therapy_group,
        )

        self.teacher = self.create_user_with_role(
            "planning_teacher",
            self.teacher_group,
        )

        self.assigner = User.objects.create_user(
            username="planning_assigner",
            password="test-password",
        )

        self.student = Student.objects.create(
            institutional_code="PLAN-001",
            first_name="Estudiante",
            last_name="Planificacion",
            date_of_birth="2014-05-10",
            admission_date="2025-01-15",
        )

        self.inactive_student = Student.objects.create(
            institutional_code="PLAN-002",
            first_name="Estudiante",
            last_name="Inactivo",
            date_of_birth="2013-04-08",
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
            self.other_psychologist,
            "PSICOLOGO",
        )

        self.assign_student(
            self.student,
            self.therapist,
            "TERAPEUTA",
        )

        self.assign_student(
            self.student,
            self.teacher,
            "DOCENTE",
        )

        self.assign_student(
            self.inactive_student,
            self.psychologist,
            "PSICOLOGO",
        )

        self.start_date = (
            timezone.localdate()
            + timedelta(days=7)
        )

        self.end_date = (
            self.start_date
            + timedelta(days=14)
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
        role,
    ):
        return StudentProfessionalAssignment.objects.create(
            student=student,
            professional=professional,
            professional_role=role,
            assigned_by=self.assigner,
        )

    def plans_url(
        self,
        student=None,
        context="PSICOLOGO",
    ):
        student = student or self.student

        return (
            reverse(
                "student-intervention-plans",
                kwargs={
                    "pk": student.pk,
                },
            )
            + f"?context={context}"
        )

    def plan_detail_url(
        self,
        plan,
        context="PSICOLOGO",
    ):
        return (
            reverse(
                "student-intervention-plan-detail",
                kwargs={
                    "pk": plan.student_id,
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

    def valid_payload(
        self,
        responsible=None,
        responsible_role="PSICOLOGO",
    ):
        responsible = (
            responsible
            or self.psychologist
        )

        return {
            "objectives": (
                "Fortalecer habilidades de autorregulación."
            ),
            "estimated_start_date": str(
                self.start_date
            ),
            "estimated_end_date": str(
                self.end_date
            ),
            "responsible_id": responsible.id,
            "responsible_role": responsible_role,
        }

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
            objectives="Objetivo de planificación.",
            estimated_start_date=self.start_date,
            estimated_end_date=self.end_date,
            professional_role=creator_role,
            responsible=responsible,
            responsible_role=responsible_role,
            status=plan_status,
            created_by=creator,
            updated_by=creator,
        )

    def test_psychologist_can_create_plan(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.plans_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        plan = StudentInterventionPlan.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            plan.student,
            self.student,
        )
        self.assertEqual(
            plan.professional_role,
            "PSICOLOGO",
        )
        self.assertEqual(
            plan.responsible,
            self.psychologist,
        )
        self.assertEqual(
            plan.responsible_role,
            "PSICOLOGO",
        )
        self.assertEqual(
            plan.status,
            "PLANNED",
        )
        self.assertEqual(
            plan.created_by,
            self.psychologist,
        )

    def test_therapist_can_create_plan(self):
        self.client.force_authenticate(
            user=self.therapist,
        )

        response = self.client.post(
            self.plans_url(
                context="TERAPEUTA",
            ),
            self.valid_payload(
                responsible=self.therapist,
                responsible_role="TERAPEUTA",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        plan = StudentInterventionPlan.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            plan.professional_role,
            "TERAPEUTA",
        )
        self.assertEqual(
            plan.responsible,
            self.therapist,
        )

    def test_plan_supports_single_estimated_date(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        payload = self.valid_payload()
        payload["estimated_end_date"] = None

        response = self.client.post(
            self.plans_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        plan = StudentInterventionPlan.objects.get(
            pk=response.data["id"],
        )

        self.assertIsNone(
            plan.estimated_end_date
        )

    def test_end_date_cannot_precede_start_date(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        payload = self.valid_payload()
        payload["estimated_end_date"] = str(
            self.start_date
            - timedelta(days=1)
        )

        response = self.client.post(
            self.plans_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "estimated_end_date",
            response.data,
        )

    def test_responsible_must_have_active_assignment(
        self,
    ):
        unassigned = self.create_user_with_role(
            "planning_unassigned",
            self.psychology_group,
        )

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.plans_url(),
            self.valid_payload(
                responsible=unassigned,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "responsible_id",
            response.data,
        )

    def test_responsible_role_must_match_assignment(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.plans_url(),
            self.valid_payload(
                responsible=self.therapist,
                responsible_role="PSICOLOGO",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_new_plan_must_start_as_planned(self):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        payload = self.valid_payload()
        payload["status"] = "IN_PROGRESS"

        response = self.client.post(
            self.plans_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "status",
            response.data,
        )

    def test_valid_status_progression(self):
        plan = self.create_plan()

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "status": "IN_PROGRESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.status,
            "IN_PROGRESS",
        )

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "status": "COMPLETED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.status,
            "COMPLETED",
        )

    def test_invalid_status_transition_is_rejected(
        self,
    ):
        plan = self.create_plan()

        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "status": "COMPLETED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        plan.refresh_from_db()

        self.assertEqual(
            plan.status,
            "PLANNED",
        )

    def test_responsible_can_query_and_update_assigned_plan(
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

        record_response = self.client.get(
            self.record_url(),
        )

        self.assertEqual(
            record_response.status_code,
            status.HTTP_200_OK,
        )

        planned_ids = {
            item["id"]
            for item
            in record_response.data["sections"]
            ["interventions"]["planned"]
        }

        self.assertIn(
            plan.id,
            planned_ids,
        )

        update_response = self.client.patch(
            self.plan_detail_url(plan),
            {
                "status": "IN_PROGRESS",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )

    def test_unrelated_assigned_professional_does_not_see_plan(
        self,
    ):
        plan = self.create_plan(
            creator=self.therapist,
            creator_role="TERAPEUTA",
            responsible=self.psychologist,
            responsible_role="PSICOLOGO",
        )

        self.client.force_authenticate(
            user=self.other_psychologist,
        )

        response = self.client.get(
            self.record_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        planned_ids = {
            item["id"]
            for item
            in response.data["sections"]
            ["interventions"]["planned"]
        }

        self.assertNotIn(
            plan.id,
            planned_ids,
        )

    def test_record_exposes_only_specialized_responsible_options(
        self,
    ):
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

        options = (
            response.data["sections"]
            ["interventions"]["responsible_options"]
        )

        option_pairs = {
            (
                item["professional"]["id"],
                item["professional_role"],
            )
            for item in options
        }

        self.assertIn(
            (
                self.psychologist.id,
                "PSICOLOGO",
            ),
            option_pairs,
        )

        self.assertIn(
            (
                self.therapist.id,
                "TERAPEUTA",
            ),
            option_pairs,
        )

        self.assertNotIn(
            (
                self.teacher.id,
                "DOCENTE",
            ),
            option_pairs,
        )

    def test_teacher_cannot_create_intervention_plan(
        self,
    ):
        self.client.force_authenticate(
            user=self.teacher,
        )

        response = self.client.post(
            self.plans_url(
                context="DOCENTE",
            ),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inactive_student_cannot_receive_new_plan(
        self,
    ):
        self.client.force_authenticate(
            user=self.psychologist,
        )

        response = self.client.post(
            self.plans_url(
                student=self.inactive_student,
            ),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
