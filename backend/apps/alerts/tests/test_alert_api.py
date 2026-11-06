from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.students.models import (
    Student,
    StudentInterventionPlan,
)

from apps.alerts.models import Alert, AlertEvent


User = get_user_model()


class AlertAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.psychologist_group = Group.objects.get(
            name="PSICOLOGO"
        )
        self.therapist_group = Group.objects.get(
            name="TERAPEUTA"
        )
        self.responsible_group = Group.objects.get(
            name="RESPONSABLE_INSTITUCIONAL"
        )

        self.psychologist = self.create_user(
            "psychologist",
            self.psychologist_group,
        )
        self.other_psychologist = self.create_user(
            "other_psychologist",
            self.psychologist_group,
        )
        self.therapist = self.create_user(
            "therapist",
            self.therapist_group,
        )
        self.responsible = self.create_user(
            "responsible",
            self.responsible_group,
        )

        self.student = self.create_student(
            "MIL-AL-ALERT-001",
            "Ana",
            "López",
        )

        self.other_student = self.create_student(
            "MIL-AL-ALERT-002",
            "Carlos",
            "Pérez",
        )

        self.list_url = reverse(
            "alerts-list"
        )

        self.summary_url = reverse(
            "alerts-summary"
        )

    def create_user(
        self,
        username,
        group,
    ):
        user = User.objects.create_user(
            username=username,
            password="test-password-123",
        )

        user.groups.add(group)

        return user

    def create_student(
        self,
        institutional_code,
        first_name,
        last_name,
    ):
        return Student.objects.create(
            institutional_code=institutional_code,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date(2015, 1, 1),
            admission_date=date(2024, 1, 15),
            is_active=True,
        )

    def create_plan(
        self,
        *,
        student=None,
        responsible=None,
        responsible_role="PSICOLOGO",
        status_value=(
            StudentInterventionPlan.Status.PLANNED
        ),
        start_date=None,
        end_date=None,
    ):
        today = timezone.localdate()

        responsible = (
            responsible
            or self.psychologist
        )

        return StudentInterventionPlan.objects.create(
            student=student or self.student,
            objectives=(
                "Objetivos de prueba para "
                "seguimiento operativo."
            ),
            estimated_start_date=(
                start_date
                or today - timedelta(days=1)
            ),
            estimated_end_date=end_date,
            professional_role=responsible_role,
            responsible=responsible,
            responsible_role=responsible_role,
            status=status_value,
            created_by=responsible,
            updated_by=responsible,
        )

    def authenticate(self, user):
        self.client.force_authenticate(
            user=user
        )

    def get_alerts(
        self,
        context="PSICOLOGO",
        **params,
    ):
        query = {
            "context": context,
            **params,
        }

        return self.client.get(
            self.list_url,
            query,
        )

    def test_alerts_require_authentication(self):
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

    def test_alerts_require_view_alerts_permission(self):
        permission = Permission.objects.get(
            codename="view_alerts",
            content_type__app_label="users",
        )

        self.psychologist_group.permissions.remove(
            permission
        )

        user = self.create_user(
            "without_alert_permission",
            self.psychologist_group,
        )

        self.authenticate(user)

        response = self.get_alerts()

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_delayed_start_creates_open_alert(self):
        today = timezone.localdate()

        plan = self.create_plan(
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=10)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        response = self.get_alerts()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        alert = Alert.objects.get()

        self.assertEqual(
            alert.condition,
            (
                Alert.Condition
                .INTERVENTION_START_DELAYED
            ),
        )

        self.assertEqual(
            alert.status,
            Alert.Status.OPEN,
        )

        self.assertEqual(
            alert.intervention_plan,
            plan,
        )

        self.assertEqual(
            alert.assigned_to,
            self.psychologist,
        )

        self.assertTrue(
            AlertEvent.objects.filter(
                alert=alert,
                event_type=(
                    AlertEvent.EventType.CREATED
                ),
            ).exists()
        )

    def test_overdue_plan_creates_overdue_alert(self):
        today = timezone.localdate()

        self.create_plan(
            status_value=(
                StudentInterventionPlan
                .Status
                .IN_PROGRESS
            ),
            start_date=(
                today - timedelta(days=10)
            ),
            end_date=(
                today - timedelta(days=1)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        response = self.get_alerts()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        alert = Alert.objects.get()

        self.assertEqual(
            alert.condition,
            Alert.Condition.INTERVENTION_OVERDUE,
        )

        self.assertIn(
            str(today - timedelta(days=1)),
            alert.reason,
        )

    def test_overdue_condition_has_priority(self):
        today = timezone.localdate()

        self.create_plan(
            status_value=(
                StudentInterventionPlan
                .Status
                .PLANNED
            ),
            start_date=(
                today - timedelta(days=10)
            ),
            end_date=(
                today - timedelta(days=1)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        self.get_alerts()

        alert = Alert.objects.get()

        self.assertEqual(
            alert.condition,
            Alert.Condition.INTERVENTION_OVERDUE,
        )

        self.assertEqual(
            Alert.objects.count(),
            1,
        )

    def test_alert_sync_is_idempotent(self):
        today = timezone.localdate()

        self.create_plan(
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=10)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        first_response = self.get_alerts()
        second_response = self.get_alerts()

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Alert.objects.count(),
            1,
        )

        self.assertEqual(
            AlertEvent.objects.filter(
                event_type=(
                    AlertEvent.EventType.CREATED
                ),
            ).count(),
            1,
        )

    def test_professional_only_sees_own_alerts(self):
        today = timezone.localdate()

        own_plan = self.create_plan(
            student=self.student,
            responsible=self.psychologist,
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        other_plan = self.create_plan(
            student=self.other_student,
            responsible=self.other_psychologist,
            start_date=(
                today - timedelta(days=3)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.authenticate(
            self.responsible
        )

        institutional_response = (
            self.get_alerts(
                context=(
                    "RESPONSABLE_INSTITUCIONAL"
                )
            )
        )

        self.assertEqual(
            institutional_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Alert.objects.count(),
            2,
        )

        self.authenticate(
            self.psychologist
        )

        response = self.get_alerts()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_plan_ids = {
            item["intervention_plan"]["id"]
            for item in response.data
        }

        self.assertEqual(
            returned_plan_ids,
            {own_plan.id},
        )

        self.assertNotIn(
            other_plan.id,
            returned_plan_ids,
        )

    def test_review_marks_alert_and_creates_history(self):
        today = timezone.localdate()

        self.create_plan(
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        self.get_alerts()

        alert = Alert.objects.get()

        review_url = reverse(
            "alerts-review",
            kwargs={
                "pk": alert.pk,
            },
        )

        response = self.client.patch(
            review_url,
            {},
            format="json",
            QUERY_STRING="context=PSICOLOGO",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        alert.refresh_from_db()

        self.assertEqual(
            alert.status,
            Alert.Status.REVIEWED,
        )

        self.assertEqual(
            alert.reviewed_by,
            self.psychologist,
        )

        self.assertIsNotNone(
            alert.reviewed_at
        )

        self.assertTrue(
            AlertEvent.objects.filter(
                alert=alert,
                event_type=(
                    AlertEvent.EventType.REVIEWED
                ),
                performed_by=self.psychologist,
            ).exists()
        )

    def test_alert_resolves_when_condition_disappears(self):
        today = timezone.localdate()

        plan = self.create_plan(
            status_value=(
                StudentInterventionPlan
                .Status
                .IN_PROGRESS
            ),
            start_date=(
                today - timedelta(days=10)
            ),
            end_date=(
                today - timedelta(days=1)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        self.get_alerts()

        alert = Alert.objects.get()

        plan.status = (
            StudentInterventionPlan
            .Status
            .COMPLETED
        )
        plan.updated_by = self.psychologist

        plan.save(
            update_fields=[
                "status",
                "updated_by",
                "updated_at",
            ]
        )

        self.get_alerts()

        alert.refresh_from_db()

        self.assertEqual(
            alert.status,
            Alert.Status.RESOLVED,
        )

        self.assertIsNotNone(
            alert.resolved_at
        )

        self.assertTrue(
            AlertEvent.objects.filter(
                alert=alert,
                event_type=(
                    AlertEvent.EventType.RESOLVED
                ),
            ).exists()
        )

    def test_resolved_alert_reopens_if_condition_returns(
        self,
    ):
        today = timezone.localdate()

        plan = self.create_plan(
            status_value=(
                StudentInterventionPlan
                .Status
                .IN_PROGRESS
            ),
            start_date=(
                today - timedelta(days=10)
            ),
            end_date=(
                today - timedelta(days=1)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        self.get_alerts()

        alert = Alert.objects.get()

        plan.status = (
            StudentInterventionPlan
            .Status
            .COMPLETED
        )

        plan.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.get_alerts()

        alert.refresh_from_db()

        self.assertEqual(
            alert.status,
            Alert.Status.RESOLVED,
        )

        plan.status = (
            StudentInterventionPlan
            .Status
            .IN_PROGRESS
        )

        plan.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.get_alerts()

        alert.refresh_from_db()

        self.assertEqual(
            alert.status,
            Alert.Status.OPEN,
        )

        self.assertIsNone(
            alert.reviewed_at
        )

        self.assertIsNone(
            alert.resolved_at
        )

        self.assertEqual(
            Alert.objects.count(),
            1,
        )

        self.assertTrue(
            AlertEvent.objects.filter(
                alert=alert,
                event_type=(
                    AlertEvent.EventType.REOPENED
                ),
            ).exists()
        )

    def test_summary_returns_alert_counts(self):
        today = timezone.localdate()

        self.create_plan(
            student=self.student,
            responsible=self.psychologist,
            start_date=(
                today - timedelta(days=3)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        response = self.client.get(
            self.summary_url,
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["open"],
            1,
        )
        self.assertEqual(
            response.data["reviewed"],
            0,
        )
        self.assertEqual(
            response.data["resolved"],
            0,
        )
        self.assertEqual(
            response.data["total"],
            1,
        )

    def test_multirole_user_must_send_context(self):
        user = User.objects.create_user(
            username="multirole-alert-user",
            password="test-password-123",
        )

        user.groups.add(
            self.psychologist_group,
            self.therapist_group,
        )

        self.authenticate(user)

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

    def test_responsible_context_sees_all_alerts(self):
        today = timezone.localdate()

        self.create_plan(
            student=self.student,
            responsible=self.psychologist,
            responsible_role="PSICOLOGO",
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.create_plan(
            student=self.other_student,
            responsible=self.therapist,
            responsible_role="TERAPEUTA",
            start_date=(
                today - timedelta(days=3)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.authenticate(
            self.responsible
        )

        response = self.get_alerts(
            context="RESPONSABLE_INSTITUCIONAL"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertEqual(
            Alert.objects.count(),
            2,
        )

    def test_alert_is_reassigned_to_new_responsible(self):
        today = timezone.localdate()

        plan = self.create_plan(
            responsible=self.psychologist,
            start_date=(
                today - timedelta(days=2)
            ),
            end_date=(
                today + timedelta(days=5)
            ),
        )

        self.authenticate(
            self.psychologist
        )

        self.get_alerts()

        alert = Alert.objects.get()

        self.assertEqual(
            alert.assigned_to,
            self.psychologist,
        )

        plan.responsible = (
            self.other_psychologist
        )
        plan.updated_by = (
            self.other_psychologist
        )

        plan.save(
            update_fields=[
                "responsible",
                "updated_by",
                "updated_at",
            ]
        )

        self.authenticate(
            self.other_psychologist
        )

        response = self.get_alerts()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        alert.refresh_from_db()

        self.assertEqual(
            alert.assigned_to,
            self.other_psychologist,
        )

        self.assertTrue(
            AlertEvent.objects.filter(
                alert=alert,
                event_type=(
                    AlertEvent.EventType.REASSIGNED
                ),
            ).exists()
        )
