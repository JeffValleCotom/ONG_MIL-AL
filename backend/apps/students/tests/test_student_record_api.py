from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.academic.models import AcademicFollowUp
from apps.psychology.models import PsychologicalFollowUp
from apps.therapy.models import TherapyFollowUp
from apps.students.models import (
    Student,
    StudentProfessionalAssignment,
)
from django.utils import timezone

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

        self.assertTrue(
            response.data["capabilities"][
                "manage_academic"
            ]
        )

    def test_docente_without_manage_academic_permission_has_no_manage_capability(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_no_academic_manage",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        docente_group = Group.objects.get(
            name="DOCENTE",
        )

        docente_group.permissions.remove(
            Permission.objects.get(
                codename="manage_academic_followups",
            )
        )

        self.client.force_authenticate(
            user=docente,
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

        self.assertIn(
            "academic",
            response.data["sections"],
        )

        self.assertFalse(
            response.data["capabilities"][
                "manage_academic"
            ]
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

    def test_responsible_record_contains_authorized_sections_only(
        self,
    ):
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
                "family",
                "assignments",
            }
        )

        self.assertEqual(
            response.data["sections"]["assignments"]["items"],
            [],
        )

        self.assertEqual(
            response.data["sections"]["family"]["items"],
            [],
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

    def create_academic_followup(
            self,
            student,
            author,
        ):

        return AcademicFollowUp.objects.create(
            student=student,
            followup_date="2026-10-20",
            academic_period="2026 - Ciclo 2",
            subject="Matemática",
            observations=(
                "Presenta avances en razonamiento lógico."
            ),
            strengths="Participación constante.",
            areas_for_improvement=(
                "Reforzar operaciones básicas."
            ),
            recommendations=(
                "Continuar con ejercicios prácticos."
            ),
            created_by=author,
            updated_by=author,
        )

    def create_psychological_followup(
        self,
        student,
        author,
    ):
        return PsychologicalFollowUp.objects.create(
            student=student,
            followup_date="2026-10-20",
            reason="Seguimiento emocional",
            observations=(
                "Presenta estabilidad durante el seguimiento."
            ),
            emotional_behavioral_notes=(
                "Respuesta emocional adecuada."
            ),
            recommendations=(
                "Mantener seguimiento psicológico."
            ),
            created_by=author,
            updated_by=author,
        )

    def create_therapy_followup(
        self,
        student,
        author,
    ):
        return TherapyFollowUp.objects.create(
            student=student,
            followup_date="2026-10-20",
            therapy_area="Terapia ocupacional",
            objectives="Fortalecer autonomía funcional.",
            activities="Actividades de coordinación.",
            progress_notes="Presenta progreso favorable.",
            recommendations="Continuar ejercicios.",
            created_by=author,
            updated_by=author,
        )

    def test_docente_record_includes_academic_section(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_academic",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        followup = self.create_academic_followup(
            student=self.student_ana,
            author=docente,
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

        self.assertIn(
            "academic",
            response.data["sections"],
        )

        followups = (
            response.data["sections"]
            ["academic"]
            ["followups"]
        )

        self.assertEqual(
            len(followups),
            1,
        )

        self.assertEqual(
            followups[0]["id"],
            followup.id,
        )

        self.assertEqual(
            followups[0]["subject"],
            "Matemática",
        )

    def test_responsible_record_excludes_academic_section(
        self,
    ):
        responsible = self.create_user_with_role(
            username="responsable_record_no_academic",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        docente = self.create_user_with_role(
            username="docente_record_author",
            role_name="DOCENTE",
        )

        self.create_academic_followup(
            student=self.student_ana,
            author=docente,
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

        self.assertNotIn(
            "academic",
            response.data["sections"],
        )

    def test_multi_role_psychology_context_excludes_academic_section(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_record_academic_isolation",
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
            student=self.student_ana,
        )

        self.create_academic_followup(
            student=self.student_ana,
            author=professional,
        )

        self.client.force_authenticate(
            user=professional
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["context"],
            "PSICOLOGO",
        )

        self.assertNotIn(
            "academic",
            response.data["sections"],
        )

    def test_psychologist_record_only_includes_psychological_section(
        self,
    ):
        psychologist = self.create_user_with_role(
            username="psych_record_section",
            role_name="PSICOLOGO",
        )

        self.assign_student(
            professional=psychologist,
            professional_role="PSICOLOGO",
            student=self.student_ana,
        )

        followup = self.create_psychological_followup(
            student=self.student_ana,
            author=psychologist,
        )

        self.client.force_authenticate(
            user=psychologist,
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "psychological",
            response.data["sections"],
        )

        self.assertNotIn(
            "academic",
            response.data["sections"],
        )

        self.assertNotIn(
            "therapy",
            response.data["sections"],
        )

        followups = (
            response.data["sections"]
            ["psychological"]
            ["followups"]
        )

        self.assertEqual(
            len(followups),
            1,
        )

        self.assertEqual(
            followups[0]["id"],
            followup.id,
        )

    def test_therapist_record_only_includes_therapy_section(
        self,
    ):
        therapist = self.create_user_with_role(
            username="therapist_record_section",
            role_name="TERAPEUTA",
        )

        self.assign_student(
            professional=therapist,
            professional_role="TERAPEUTA",
            student=self.student_ana,
        )

        followup = self.create_therapy_followup(
            student=self.student_ana,
            author=therapist,
        )

        self.client.force_authenticate(
            user=therapist,
        )

        response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "TERAPEUTA",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "therapy",
            response.data["sections"],
        )

        self.assertNotIn(
            "academic",
            response.data["sections"],
        )

        self.assertNotIn(
            "psychological",
            response.data["sections"],
        )

        followups = (
            response.data["sections"]
            ["therapy"]
            ["followups"]
        )

        self.assertEqual(
            len(followups),
            1,
        )

        self.assertEqual(
            followups[0]["id"],
            followup.id,
        )

    def test_multi_role_psychology_and_therapy_remain_isolated(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_psych_therapy_record",
            password="MilalRecord123!",
        )

        professional.groups.add(
            Group.objects.get(name="PSICOLOGO"),
            Group.objects.get(name="TERAPEUTA"),
        )

        self.assign_student(
            professional=professional,
            professional_role="PSICOLOGO",
            student=self.student_ana,
        )

        self.assign_student(
            professional=professional,
            professional_role="TERAPEUTA",
            student=self.student_ana,
        )

        self.create_psychological_followup(
            student=self.student_ana,
            author=professional,
        )

        self.create_therapy_followup(
            student=self.student_ana,
            author=professional,
        )

        self.client.force_authenticate(
            user=professional,
        )

        psychology_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            psychology_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "psychological",
            psychology_response.data["sections"],
        )

        self.assertNotIn(
            "therapy",
            psychology_response.data["sections"],
        )

        therapy_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "TERAPEUTA",
            },
        )

        self.assertEqual(
            therapy_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "therapy",
            therapy_response.data["sections"],
        )

        self.assertNotIn(
            "psychological",
            therapy_response.data["sections"],
        )

    def test_responsible_record_includes_assignment_history(
        self,
    ):
        responsible = self.create_user_with_role(
            username="responsable_integral_record",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        docente = self.create_user_with_role(
            username="docente_integral_record",
            role_name="DOCENTE",
        )

        active_assignment = self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        finished_assignment = (
            StudentProfessionalAssignment.objects.create(
                student=self.student_ana,
                professional=docente,
                professional_role="DOCENTE",
                assigned_by=self.assignment_manager,
                is_active=False,
                unassigned_at=timezone.now(),
            )
        )

        self.client.force_authenticate(
            user=responsible,
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

        self.assertIn(
            "assignments",
            response.data["sections"],
        )

        items = (
            response.data["sections"]
            ["assignments"]
            ["items"]
        )

        returned_ids = {
            item["id"]
            for item in items
        }

        self.assertEqual(
            returned_ids,
            {
                active_assignment.id,
                finished_assignment.id,
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

    def test_professional_record_excludes_assignments_section(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_no_assignments",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.client.force_authenticate(
            user=docente,
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

        self.assertNotIn(
            "assignments",
            response.data["sections"],
        )

    def test_multi_role_assignment_section_respects_context(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_responsible_docente_record",
            password="MilalRecord123!",
        )

        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            ),
        )

        self.assign_student(
            professional=professional,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.create_academic_followup(
            student=self.student_ana,
            author=professional,
        )

        self.client.force_authenticate(
            user=professional,
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
        self.assertIn(
            "academic",
            docente_response.data["sections"],
        )
        self.assertNotIn(
            "assignments",
            docente_response.data["sections"],
        )

        responsible_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            responsible_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "assignments",
            responsible_response.data["sections"],
        )
        self.assertNotIn(
            "academic",
            responsible_response.data["sections"],
        )

    def test_record_only_includes_followups_created_by_current_user(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_record_owner",
            password="MilalRecord123!",
        )

        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
            Group.objects.get(name="TERAPEUTA"),
        )

        other_docente = self.create_user_with_role(
            username="other_docente_record_owner",
            role_name="DOCENTE",
        )

        other_psychologist = self.create_user_with_role(
            username="other_psych_record_owner",
            role_name="PSICOLOGO",
        )

        other_therapist = self.create_user_with_role(
            username="other_therapy_record_owner",
            role_name="TERAPEUTA",
        )

        for role in (
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
        ):
            self.assign_student(
                professional=professional,
                professional_role=role,
                student=self.student_ana,
            )

        self.assign_student(
            professional=other_docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        self.assign_student(
            professional=other_psychologist,
            professional_role="PSICOLOGO",
            student=self.student_ana,
        )

        self.assign_student(
            professional=other_therapist,
            professional_role="TERAPEUTA",
            student=self.student_ana,
        )

        own_academic = self.create_academic_followup(
            student=self.student_ana,
            author=professional,
        )

        other_academic = self.create_academic_followup(
            student=self.student_ana,
            author=other_docente,
        )

        own_psychological = (
            self.create_psychological_followup(
                student=self.student_ana,
                author=professional,
            )
        )

        other_psychological = (
            self.create_psychological_followup(
                student=self.student_ana,
                author=other_psychologist,
            )
        )

        own_therapy = self.create_therapy_followup(
            student=self.student_ana,
            author=professional,
        )

        other_therapy = self.create_therapy_followup(
            student=self.student_ana,
            author=other_therapist,
        )

        self.client.force_authenticate(
            user=professional,
        )

        academic_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            academic_response.status_code,
            status.HTTP_200_OK,
        )

        academic_ids = {
            item["id"]
            for item in (
                academic_response.data["sections"]
                ["academic"]
                ["followups"]
            )
        }

        self.assertEqual(
            academic_ids,
            {
                own_academic.id,
            },
        )

        self.assertNotIn(
            other_academic.id,
            academic_ids,
        )

        psychological_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "PSICOLOGO",
            },
        )

        self.assertEqual(
            psychological_response.status_code,
            status.HTTP_200_OK,
        )

        psychological_ids = {
            item["id"]
            for item in (
                psychological_response.data["sections"]
                ["psychological"]
                ["followups"]
            )
        }

        self.assertEqual(
            psychological_ids,
            {
                own_psychological.id,
            },
        )

        self.assertNotIn(
            other_psychological.id,
            psychological_ids,
        )

        therapy_response = self.client.get(
            self.record_url(self.student_ana),
            {
                "context": "TERAPEUTA",
            },
        )

        self.assertEqual(
            therapy_response.status_code,
            status.HTTP_200_OK,
        )

        therapy_ids = {
            item["id"]
            for item in (
                therapy_response.data["sections"]
                ["therapy"]
                ["followups"]
            )
        }

        self.assertEqual(
            therapy_ids,
            {
                own_therapy.id,
            },
        )

        self.assertNotIn(
            other_therapy.id,
            therapy_ids,
        )

    def test_record_sections_require_role_bound_functional_permissions(
        self,
    ):
        professional = User.objects.create_user(
            username="multi_record_permissions",
            password="MilalRecord123!",
        )

        docente_group = Group.objects.get(
            name="DOCENTE",
        )
        psychology_group = Group.objects.get(
            name="PSICOLOGO",
        )
        therapy_group = Group.objects.get(
            name="TERAPEUTA",
        )

        professional.groups.add(
            docente_group,
            psychology_group,
            therapy_group,
        )

        for role in (
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
        ):
            self.assign_student(
                professional=professional,
                professional_role=role,
                student=self.student_ana,
            )

        docente_group.permissions.remove(
            Permission.objects.get(
                codename="view_academic_followups",
            )
        )

        psychology_group.permissions.remove(
            Permission.objects.get(
                codename="view_psychological_followups",
            )
        )

        therapy_group.permissions.remove(
            Permission.objects.get(
                codename="view_therapy_followups",
            )
        )

        self.client.force_authenticate(
            user=professional,
        )

        context_sections = {
            "DOCENTE": "academic",
            "PSICOLOGO": "psychological",
            "TERAPEUTA": "therapy",
        }

        for context, restricted_section in (
            context_sections.items()
        ):
            response = self.client.get(
                self.record_url(self.student_ana),
                {
                    "context": context,
                },
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

            self.assertIn(
                "general",
                response.data["sections"],
            )

            self.assertNotIn(
                restricted_section,
                response.data["sections"],
            )

    def test_assigned_professional_can_consult_inactive_student_history(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_inactive_record",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
            student=self.student_ana,
        )

        followup = self.create_academic_followup(
            student=self.student_ana,
            author=docente,
        )

        self.student_ana.is_active = False
        self.student_ana.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        self.client.force_authenticate(
            user=docente,
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

        self.assertFalse(
            response.data["sections"]
            ["general"]
            ["is_active"]
        )

        returned_ids = {
            item["id"]
            for item in (
                response.data["sections"]
                ["academic"]
                ["followups"]
            )
        }

        self.assertIn(
            followup.id,
            returned_ids,
        )

    def test_responsible_record_can_update_general_information(
        self,
    ):
        responsible = self.create_user_with_role(
            username="responsible_record_update",
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
        self.assertTrue(
            response.data["capabilities"]["update_general"]
        )
        self.assertTrue(
            response.data["capabilities"]["manage_family"]
        )


    def test_responsible_without_manage_students_cannot_update_general(
        self,
    ):
        responsible = self.create_user_with_role(
            username="responsible_record_no_update",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        responsible_group = Group.objects.get(
            name="RESPONSABLE_INSTITUCIONAL"
        )
        responsible_group.permissions.remove(
            Permission.objects.get(
                content_type__app_label="users",
                content_type__model="user",
                codename="manage_students",
            )
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
        self.assertFalse(
            response.data["capabilities"]["update_general"]
        )
        self.assertFalse(
            response.data["capabilities"]["manage_family"]
        )


    def test_professional_record_cannot_update_general_information(
        self,
    ):
        docente = self.create_user_with_role(
            username="docente_record_no_general_update",
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
        self.assertFalse(
            response.data["capabilities"]["update_general"]
        )
        self.assertFalse(
            response.data["capabilities"]["manage_family"]
        )
