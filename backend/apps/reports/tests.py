from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.psychology.models import PsychologicalFollowUp
from apps.students.models import (
    Student,
    StudentIntervention,
    StudentInterventionFollowUp,
    StudentInterventionPlan,
    StudentProfessionalAssignment,
)
from apps.therapy.models import TherapyFollowUp

from .models import StudentReport


User = get_user_model()


class StudentReportAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_group = Group.objects.get(
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

        cls.responsible = cls.create_user(
            "report_responsible",
            cls.responsible_group,
        )

        cls.teacher = cls.create_user(
            "report_teacher",
            cls.teacher_group,
        )

        cls.other_teacher = cls.create_user(
            "report_other_teacher",
            cls.teacher_group,
        )

        cls.psychologist = cls.create_user(
            "report_psychologist",
            cls.psychologist_group,
        )

        cls.therapist = cls.create_user(
            "report_therapist",
            cls.therapist_group,
        )

        cls.multi_role_user = cls.create_user(
            "report_multi_role",
            cls.teacher_group,
            cls.therapist_group,
        )

        cls.student = Student.objects.create(
            institutional_code="MIL-RPT-001",
            first_name="Ana",
            last_name="Reporte",
            date_of_birth=date(2012, 4, 10),
            admission_date=date(2025, 1, 15),
            is_active=True,
        )

        cls.second_student = Student.objects.create(
            institutional_code="MIL-RPT-002",
            first_name="Mario",
            last_name="Segundo",
            date_of_birth=date(2013, 5, 20),
            admission_date=date(2025, 2, 10),
            is_active=True,
        )

        cls.unassigned_student = Student.objects.create(
            institutional_code="MIL-RPT-003",
            first_name="Sofia",
            last_name="NoAsignada",
            date_of_birth=date(2011, 7, 15),
            admission_date=date(2025, 3, 5),
            is_active=True,
        )

        cls.assign_student(
            cls.student,
            cls.teacher,
            "DOCENTE",
        )
        cls.assign_student(
            cls.student,
            cls.other_teacher,
            "DOCENTE",
        )
        cls.assign_student(
            cls.student,
            cls.psychologist,
            "PSICOLOGO",
        )
        cls.assign_student(
            cls.student,
            cls.therapist,
            "TERAPEUTA",
        )
        cls.assign_student(
            cls.student,
            cls.multi_role_user,
            "DOCENTE",
        )
        cls.assign_student(
            cls.student,
            cls.multi_role_user,
            "TERAPEUTA",
        )

        cls.assign_student(
            cls.second_student,
            cls.teacher,
            "DOCENTE",
        )

        cls.academic_followup = (
            AcademicFollowUp.objects.create(
                student=cls.student,
                followup_date=date(2026, 1, 10),
                academic_period="2026 - Ciclo 1",
                subject="Matemática",
                observations=(
                    "Presenta avances en resolución "
                    "de ejercicios."
                ),
                strengths=(
                    "Participación y disposición "
                    "para aprender."
                ),
                areas_for_improvement=(
                    "Reforzar razonamiento lógico."
                ),
                recommendations=(
                    "Continuar con ejercicios guiados."
                ),
                created_by=cls.teacher,
                updated_by=cls.teacher,
            )
        )

        cls.old_academic_followup = (
            AcademicFollowUp.objects.create(
                student=cls.student,
                followup_date=date(2025, 12, 1),
                academic_period="2025 - Ciclo 2",
                subject="Matemática",
                observations="Registro histórico.",
                strengths="Participación.",
                areas_for_improvement="Práctica.",
                recommendations="Continuar seguimiento.",
                created_by=cls.teacher,
                updated_by=cls.teacher,
            )
        )

        cls.psychological_followup = (
            PsychologicalFollowUp.objects.create(
                student=cls.student,
                followup_date=date(2026, 1, 11),
                reason="Seguimiento emocional",
                observations=(
                    "Se observa mejor disposición."
                ),
                emotional_behavioral_notes=(
                    "Mayor autorregulación."
                ),
                recommendations=(
                    "Mantener acompañamiento."
                ),
                created_by=cls.psychologist,
                updated_by=cls.psychologist,
            )
        )

        cls.therapy_followup = (
            TherapyFollowUp.objects.create(
                student=cls.student,
                followup_date=date(2026, 1, 12),
                therapy_area="Lenguaje",
                objectives=(
                    "Fortalecer comunicación funcional."
                ),
                activities=(
                    "Ejercicios de expresión oral."
                ),
                progress_notes=(
                    "Muestra avances en expresión."
                ),
                recommendations=(
                    "Continuar práctica en casa."
                ),
                created_by=cls.therapist,
                updated_by=cls.therapist,
            )
        )

        cls.evaluation = Evaluation.objects.create(
            student=cls.student,
            evaluation_date=date(2026, 1, 13),
            evaluation_type="Evaluación funcional",
            results="Evolución favorable.",
            observations="Continuar seguimiento.",
            professional_role="TERAPEUTA",
            created_by=cls.therapist,
            updated_by=cls.therapist,
        )

        cls.intervention = (
            StudentIntervention.objects.create(
                student=cls.student,
                intervention_date=date(2026, 1, 14),
                professional_role="PSICOLOGO",
                objectives=(
                    "Fortalecer autorregulación."
                ),
                observations=(
                    "Participa activamente."
                ),
                created_by=cls.psychologist,
                updated_by=cls.psychologist,
            )
        )

        cls.intervention_plan = (
            StudentInterventionPlan.objects.create(
                student=cls.student,
                objectives=(
                    "Mejorar estrategias de regulación."
                ),
                estimated_start_date=date(
                    2026,
                    1,
                    15,
                ),
                estimated_end_date=date(
                    2026,
                    2,
                    15,
                ),
                professional_role="PSICOLOGO",
                responsible=cls.psychologist,
                responsible_role="PSICOLOGO",
                status="IN_PROGRESS",
                created_by=cls.psychologist,
                updated_by=cls.psychologist,
            )
        )

        cls.intervention_followup = (
            StudentInterventionFollowUp.objects.create(
                intervention_plan=(
                    cls.intervention_plan
                ),
                followup_date=date(2026, 1, 16),
                progress=(
                    "Mayor participación y "
                    "autorregulación."
                ),
                results=(
                    "Cumple parcialmente los objetivos."
                ),
                observations=(
                    "Continuar seguimiento semanal."
                ),
                status="IN_PROGRESS",
                created_by=cls.psychologist,
            )
        )

    @classmethod
    def create_user(
        cls,
        username,
        *groups,
    ):
        user = User.objects.create_user(
            username=username,
            password="test-password",
            first_name=username,
            last_name="MIL-AL",
        )

        user.groups.add(*groups)

        return user

    @classmethod
    def assign_student(
        cls,
        student,
        professional,
        role,
    ):
        return (
            StudentProfessionalAssignment.objects.create(
                student=student,
                professional=professional,
                professional_role=role,
                assigned_by=cls.responsible,
                is_active=True,
            )
        )

    def generate_report(
        self,
        *,
        user=None,
        context="DOCENTE",
        student=None,
        report_type="ACADEMIC",
        date_from=None,
        date_to=None,
    ):
        user = user or self.teacher
        student = student or self.student

        self.client.force_authenticate(
            user=user,
        )

        payload = {
            "student_id": student.id,
            "report_type": report_type,
        }

        if date_from is not None:
            payload["date_from"] = str(
                date_from
            )

        if date_to is not None:
            payload["date_to"] = str(
                date_to
            )

        return self.client.post(
            (
                reverse("report-list")
                + f"?context={context}"
            ),
            payload,
            format="json",
        )

    def list_reports(
        self,
        *,
        user=None,
        context="DOCENTE",
        **filters,
    ):
        self.client.force_authenticate(
            user=user or self.teacher,
        )

        params = {
            "context": context,
            **filters,
        }

        return self.client.get(
            reverse("report-list"),
            params,
        )

    def detail_report(
        self,
        report,
        *,
        user=None,
        context="DOCENTE",
    ):
        self.client.force_authenticate(
            user=user or self.teacher,
        )

        return self.client.get(
            reverse(
                "report-detail",
                kwargs={
                    "pk": report.pk,
                },
            ),
            {
                "context": context,
            },
        )

    def export_report(
        self,
        report,
        *,
        user=None,
        context="DOCENTE",
    ):
        self.client.force_authenticate(
            user=user or self.teacher,
        )

        return self.client.get(
            reverse(
                "report-export",
                kwargs={
                    "pk": report.pk,
                },
            ),
            {
                "context": context,
            },
        )

    # HU-20 / TASK-120

    def test_teacher_can_generate_academic_report(self):
        response = self.generate_report(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            report.generated_by,
            self.teacher,
        )
        self.assertEqual(
            report.generated_role,
            "DOCENTE",
        )
        self.assertEqual(
            report.report_type,
            "ACADEMIC",
        )

        self.assertNotIn(
            "content_snapshot",
            response.data,
        )

        sections = (
            report.content_snapshot["sections"]
        )

        self.assertIn(
            "academic",
            sections,
        )

    def test_report_period_filters_source_records(self):
        response = self.generate_report(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        academic = (
            report.content_snapshot
            ["sections"]
            ["academic"]
        )

        self.assertEqual(
            len(academic),
            1,
        )
        self.assertEqual(
            academic[0]["id"],
            self.academic_followup.id,
        )

    def test_invalid_period_is_rejected_for_generation_and_filters(
        self,
    ):
        create_response = self.generate_report(
            date_from=date(2026, 2, 1),
            date_to=date(2026, 1, 1),
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        list_response = self.list_reports(
            date_from="2026-02-01",
            date_to="2026-01-01",
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_teacher_cannot_generate_psychological_report(
        self,
    ):
        response = self.generate_report(
            report_type="PSYCHOLOGICAL",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            StudentReport.objects.filter(
                generated_by=self.teacher,
                report_type="PSYCHOLOGICAL",
            ).exists()
        )

    def test_professional_cannot_generate_for_unassigned_student(
        self,
    ):
        response = self.generate_report(
            student=self.unassigned_student,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # HU-21 / TASK-126

    def test_list_omits_snapshot_and_detail_returns_it(
        self,
    ):
        create_response = self.generate_report()

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        list_response = self.list_reports()

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )

        items = list_response.data["items"]

        self.assertEqual(
            len(items),
            1,
        )
        self.assertNotIn(
            "content_snapshot",
            items[0],
        )

        detail_response = self.detail_report(
            report,
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "content_snapshot",
            detail_response.data,
        )

    def test_report_filters_by_student_type_and_generation_date(
        self,
    ):
        first = self.generate_report(
            report_type="ACADEMIC",
        )

        self.assertEqual(
            first.status_code,
            status.HTTP_201_CREATED,
        )

        second = self.generate_report(
            report_type="INTEGRAL",
        )

        self.assertEqual(
            second.status_code,
            status.HTTP_201_CREATED,
        )

        third = self.generate_report(
            student=self.second_student,
            report_type="ACADEMIC",
        )

        self.assertEqual(
            third.status_code,
            status.HTTP_201_CREATED,
        )

        today = str(
            timezone.localdate()
        )

        response = self.list_reports(
            student=self.student.id,
            report_type="ACADEMIC",
            date_from=today,
            date_to=today,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        items = response.data["items"]

        self.assertEqual(
            len(items),
            1,
        )
        self.assertEqual(
            items[0]["id"],
            first.data["id"],
        )

    def test_only_creator_can_list_and_open_report(
        self,
    ):
        create_response = self.generate_report()

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        other_list = self.list_reports(
            user=self.other_teacher,
            context="DOCENTE",
        )

        self.assertEqual(
            other_list.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            other_list.data["items"],
            [],
        )

        detail_response = self.detail_report(
            report,
            user=self.other_teacher,
            context="DOCENTE",
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_multirole_report_is_isolated_by_generation_context(
        self,
    ):
        create_response = self.generate_report(
            user=self.multi_role_user,
            context="DOCENTE",
            report_type="INTEGRAL",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        teacher_list = self.list_reports(
            user=self.multi_role_user,
            context="DOCENTE",
        )

        self.assertEqual(
            len(
                teacher_list.data["items"]
            ),
            1,
        )

        therapy_list = self.list_reports(
            user=self.multi_role_user,
            context="TERAPEUTA",
        )

        self.assertEqual(
            therapy_list.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            therapy_list.data["items"],
            [],
        )

        therapy_detail = self.detail_report(
            report,
            user=self.multi_role_user,
            context="TERAPEUTA",
        )

        self.assertEqual(
            therapy_detail.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_can_export_pdf(self):
        create_response = self.generate_report()

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        response = self.export_report(
            report,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )
        self.assertIn(
            ".pdf",
            response["Content-Disposition"],
        )
        self.assertTrue(
            response.content.startswith(
                b"%PDF-"
            )
        )

    def test_other_assigned_user_cannot_export_report(
        self,
    ):
        create_response = self.generate_report()

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        response = self.export_report(
            report,
            user=self.other_teacher,
            context="DOCENTE",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_snapshot_is_preserved_after_source_changes(
        self,
    ):
        original_observations = (
            self.academic_followup.observations
        )

        create_response = self.generate_report(
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 31),
        )

        report = StudentReport.objects.get(
            pk=create_response.data["id"],
        )

        self.academic_followup.observations = (
            "Información modificada después "
            "de generar el reporte."
        )
        self.academic_followup.save(
            update_fields=[
                "observations",
            ],
        )

        detail_response = self.detail_report(
            report,
        )

        academic = (
            detail_response.data
            ["content_snapshot"]
            ["sections"]
            ["academic"]
        )

        self.assertEqual(
            academic[0]["observations"],
            original_observations,
        )

    # HU-22 / TASK-132

    def test_teacher_integral_report_contains_only_teacher_context_sections(
        self,
    ):
        response = self.generate_report(
            report_type="INTEGRAL",
            date_from=date(2026, 1, 1),
            date_to=date(2026, 2, 28),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        snapshot = report.content_snapshot
        sections = snapshot["sections"]

        expected_sections = {
            "academic",
            "evaluations",
        }

        self.assertEqual(
            set(sections.keys()),
            expected_sections,
        )

        sections = (
    report.content_snapshot[
        "sections"
    ]
)

        expected_sections = {
            "academic",
            "evaluations",
        }

        self.assertEqual(
            set(sections.keys()),
            expected_sections,
        )

        self.assertIn(
            "academic",
            sections,
        )

        self.assertIn(
            "evaluations",
            sections,
        )

        self.assertNotIn(
            "psychological",
            sections,
        )

        self.assertNotIn(
            "therapy",
            sections,
        )

        self.assertNotIn(
            "performed_interventions",
            sections,
        )

        self.assertNotIn(
            "planned_interventions",
            sections,
        )

        highlights = (
            snapshot["summary"]["highlights"]
        )

    def test_psychologist_can_generate_integral_report(
        self,
    ):
        response = self.generate_report(
            user=self.psychologist,
            context="PSICOLOGO",
            report_type="INTEGRAL",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            report.generated_role,
            "PSICOLOGO",
        )

    def test_therapist_can_generate_integral_report(
        self,
    ):
        response = self.generate_report(
            user=self.therapist,
            context="TERAPEUTA",
            report_type="INTEGRAL",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            report.generated_role,
            "TERAPEUTA",
        )

    def test_responsible_can_generate_general_report(
        self,
    ):
        response = self.generate_report(
            user=self.responsible,
            context="RESPONSABLE_INSTITUCIONAL",
            report_type="GENERAL",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        report = StudentReport.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            report.generated_role,
            "RESPONSABLE_INSTITUCIONAL",
        )
        self.assertIn(
            "general",
            report.content_snapshot["sections"],
        )
