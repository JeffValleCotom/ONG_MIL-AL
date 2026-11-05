from copy import deepcopy
from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academic.models import AcademicFollowUp
from apps.evaluations.models import Evaluation
from apps.reports.models import StudentReport
from apps.students.models import (
    Student,
    StudentIntervention,
    StudentProfessionalAssignment,
)

from .context import build_ai_context
from .models import AIInsight
from .providers import (
    AIProviderError,
    AIProviderResult,
)


User = get_user_model()


class DummyAIProvider:
    provider_name = "test-provider"
    model = "test-model"

    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        schema_name,
        schema,
        max_output_tokens=1500,
    ):
        del (
            system_prompt,
            user_prompt,
            schema,
            max_output_tokens,
        )

        results = {
            "student_analysis": {
                "summary": (
                    "Resumen de análisis de prueba."
                ),
                "trends": [
                    {
                        "area": "ACADEMIC",
                        "observation": (
                            "Se observa una tendencia "
                            "académica registrada."
                        ),
                        "evidence": [
                            "Seguimiento académico."
                        ],
                    }
                ],
                "progress": [
                    {
                        "area": "ACADEMIC",
                        "observation": (
                            "Se observan avances."
                        ),
                        "evidence": [
                            "Fortaleza registrada."
                        ],
                    }
                ],
                "attention_points": [
                    {
                        "area": "ACADEMIC",
                        "observation": (
                            "Conviene revisar un área "
                            "de mejora registrada."
                        ),
                        "evidence": [
                            "Área de mejora."
                        ],
                    }
                ],
            },
            "followup_suggestions": {
                "summary": (
                    "Resumen de sugerencias."
                ),
                "suggestions": [
                    {
                        "title": (
                            "Revisar evolución reciente"
                        ),
                        "rationale": (
                            "Existe información "
                            "registrada para revisar."
                        ),
                        "related_data": [
                            "Seguimiento disponible."
                        ],
                    }
                ],
            },
            "intervention_recommendations": {
                "summary": (
                    "Resumen de recomendaciones."
                ),
                "recommendations": [
                    {
                        "objective": (
                            "Fortalecer el seguimiento."
                        ),
                        "action": (
                            "Revisar los objetivos "
                            "registrados."
                        ),
                        "rationale": (
                            "La información disponible "
                            "permite considerar esta "
                            "acción."
                        ),
                        "related_data": [
                            "Registro relacionado."
                        ],
                        "cautions": [
                            "Requiere criterio profesional."
                        ],
                    }
                ],
            },
            "report_suggestions": {
                "summary": (
                    "Contenido de apoyo para reporte."
                ),
                "suggested_sections": [
                    {
                        "section": "Observaciones",
                        "draft_text": (
                            "Texto sugerido por IA."
                        ),
                        "rationale": (
                            "Resume información "
                            "registrada."
                        ),
                    }
                ],
            },
        }

        return AIProviderResult(
            data=results[schema_name],
            provider=self.provider_name,
            model=self.model,
            response_id="resp_test_123",
            usage={
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            },
        )


class AIInsightAPITests(APITestCase):
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

        cls.assigner = User.objects.create_user(
            username="ai_assigner",
            password="test-password",
        )

        cls.teacher = cls.create_user(
            "ai_teacher",
            cls.teacher_group,
        )

        cls.other_teacher = cls.create_user(
            "ai_other_teacher",
            cls.teacher_group,
        )

        cls.psychologist = cls.create_user(
            "ai_psychologist",
            cls.psychologist_group,
        )

        cls.therapist = cls.create_user(
            "ai_therapist",
            cls.therapist_group,
        )

        cls.multi_role_user = cls.create_user(
            "ai_multi_role",
            cls.teacher_group,
            cls.therapist_group,
        )

        cls.student = Student.objects.create(
            institutional_code="MIL-AI-001",
            first_name="Ana",
            last_name="Inteligencia",
            date_of_birth=date(
                2012,
                4,
                10,
            ),
            admission_date=date(
                2025,
                1,
                15,
            ),
            is_active=True,
        )

        cls.unassigned_student = (
            Student.objects.create(
                institutional_code="MIL-AI-002",
                first_name="Mario",
                last_name="NoAsignado",
                date_of_birth=date(
                    2013,
                    5,
                    20,
                ),
                admission_date=date(
                    2025,
                    2,
                    10,
                ),
                is_active=True,
            )
        )

        cls.assign_student(
            cls.teacher,
            "DOCENTE",
        )

        cls.assign_student(
            cls.other_teacher,
            "DOCENTE",
        )

        cls.assign_student(
            cls.psychologist,
            "PSICOLOGO",
        )

        cls.assign_student(
            cls.therapist,
            "TERAPEUTA",
        )

        cls.assign_student(
            cls.multi_role_user,
            "DOCENTE",
        )

        cls.assign_student(
            cls.multi_role_user,
            "TERAPEUTA",
        )

        cls.academic_followup = (
            AcademicFollowUp.objects.create(
                student=cls.student,
                followup_date=date(
                    2026,
                    10,
                    15,
                ),
                academic_period=(
                    "2026 - Ciclo 2"
                ),
                subject="Matemática",
                observations=(
                    "Muestra participación "
                    "constante."
                ),
                strengths=(
                    "Resolución de ejercicios."
                ),
                areas_for_improvement=(
                    "Reforzar razonamiento lógico."
                ),
                recommendations=(
                    "Continuar práctica guiada."
                ),
                created_by=cls.teacher,
                updated_by=cls.teacher,
            )
        )

        cls.evaluation = Evaluation.objects.create(
            student=cls.student,
            evaluation_date=date(
                2026,
                10,
                16,
            ),
            evaluation_type=(
                "Evaluación académica"
            ),
            results=(
                "Resultados registrados."
            ),
            observations=(
                "Continuar seguimiento."
            ),
            professional_role="DOCENTE",
            created_by=cls.teacher,
            updated_by=cls.teacher,
        )

        cls.report_snapshot = {
            "student": {
                "id": cls.student.id,
                "institutional_code": (
                    cls.student
                    .institutional_code
                ),
                "first_name": (
                    cls.student.first_name
                ),
                "last_name": (
                    cls.student.last_name
                ),
            },
            "report_type": "ACADEMIC",
            "period": {
                "date_from": "2026-10-01",
                "date_to": "2026-11-04",
            },
            "sections": {
                "academic": [
                    {
                        "id": 999,
                        "date": "2026-10-15",
                        "subject": "Matemática",
                        "observations": (
                            "Información profesional "
                            "del reporte."
                        ),
                        "responsible": {
                            "id": cls.teacher.id,
                            "username": (
                                cls.teacher.username
                            ),
                        },
                    }
                ],
            },
            "summary": {
                "total_records": 1,
            },
        }

        cls.report = StudentReport.objects.create(
            student=cls.student,
            report_type=(
                StudentReport
                .ReportType
                .ACADEMIC
            ),
            date_from=date(
                2026,
                10,
                1,
            ),
            date_to=date(
                2026,
                11,
                4,
            ),
            generated_role="DOCENTE",
            content_snapshot=(
                deepcopy(
                    cls.report_snapshot
                )
            ),
            generated_by=cls.teacher,
        )

        cls.other_report = (
            StudentReport.objects.create(
                student=cls.student,
                report_type=(
                    StudentReport
                    .ReportType
                    .ACADEMIC
                ),
                date_from=date(
                    2026,
                    10,
                    1,
                ),
                date_to=date(
                    2026,
                    11,
                    4,
                ),
                generated_role="DOCENTE",
                content_snapshot={
                    "sections": {},
                },
                generated_by=(
                    cls.other_teacher
                ),
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
        professional,
        role,
    ):
        return (
            StudentProfessionalAssignment
            .objects
            .create(
                student=cls.student,
                professional=professional,
                professional_role=role,
                assigned_by=cls.assigner,
                is_active=True,
            )
        )

    def setUp(self):
        self.provider_patcher = patch(
            (
                "apps.ai_support.services."
                "get_ai_provider"
            ),
            return_value=DummyAIProvider(),
        )

        self.provider_patcher.start()

        self.addCleanup(
            self.provider_patcher.stop
        )

    def create_insight(
        self,
        *,
        user=None,
        context="DOCENTE",
        kind="ANALYSIS",
        student_id=None,
        source_report_id=None,
        date_from=None,
        date_to=None,
    ):
        self.client.force_authenticate(
            user=user or self.teacher,
        )

        payload = {
            "kind": kind,
        }

        if student_id is not None:
            payload["student_id"] = (
                student_id
            )
        elif (
            kind != "REPORT_SUGGESTION"
        ):
            payload["student_id"] = (
                self.student.id
            )

        if source_report_id is not None:
            payload["source_report_id"] = (
                source_report_id
            )

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
                reverse(
                    "ai-insight-list"
                )
                + f"?context={context}"
            ),
            payload,
            format="json",
        )

    def review_insight(
        self,
        insight,
        *,
        user=None,
        context="DOCENTE",
        decision="ACCEPTED",
        notes="Revisión profesional.",
        edited_content=None,
    ):
        self.client.force_authenticate(
            user=user or self.teacher,
        )

        payload = {
            "decision": decision,
            "professional_notes": notes,
        }

        if edited_content is not None:
            payload["edited_content"] = (
                edited_content
            )

        return self.client.patch(
            (
                reverse(
                    "ai-insight-review",
                    kwargs={
                        "pk": insight.pk,
                    },
                )
                + f"?context={context}"
            ),
            payload,
            format="json",
        )

    # HU-23 / TASK-138

    def test_authorized_user_can_generate_analysis(
        self,
    ):
        response = self.create_insight(
            kind="ANALYSIS",
            date_from=date(
                2026,
                10,
                1,
            ),
            date_to=date(
                2026,
                11,
                4,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            insight.kind,
            AIInsight.Kind.ANALYSIS,
        )
        self.assertEqual(
            insight.generated_by,
            self.teacher,
        )
        self.assertEqual(
            insight.generated_role,
            "DOCENTE",
        )
        self.assertEqual(
            insight.review_status,
            (
                AIInsight
                .ReviewStatus
                .NOT_APPLICABLE
            ),
        )

        self.assertEqual(
            insight.provider,
            "test-provider",
        )
        self.assertEqual(
            insight.model_name,
            "test-model",
        )
        self.assertEqual(
            insight.provider_response_id,
            "resp_test_123",
        )
        self.assertEqual(
            insight.usage_json[
                "total_tokens"
            ],
            150,
        )

        self.assertIn(
            "ai_notice",
            insight.result_json,
        )
        self.assertIn(
            "trends",
            insight.result_json,
        )
        self.assertIn(
            "progress",
            insight.result_json,
        )
        self.assertIn(
            "attention_points",
            insight.result_json,
        )

    def test_ai_context_is_limited_by_professional_role(
        self,
    ):
        expected = {
            "DOCENTE": {
                "academic",
                "evaluations",
            },
            "PSICOLOGO": {
                "psychological",
                "evaluations",
                "performed_interventions",
                "planned_interventions",
            },
            "TERAPEUTA": {
                "therapy",
                "evaluations",
                "performed_interventions",
                "planned_interventions",
            },
        }

        for role, sections in expected.items():
            with self.subTest(role=role):
                context = build_ai_context(
                    student=self.student,
                    context=role,
                )

                self.assertEqual(
                    set(
                        context[
                            "sections"
                        ].keys()
                    ),
                    sections,
                )

    def test_ai_context_does_not_include_identity(
        self,
    ):
        response = self.create_insight(
            kind="ANALYSIS",
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        context_text = str(
            insight.context_snapshot
        )

        self.assertNotIn(
            self.student.institutional_code,
            context_text,
        )
        self.assertNotIn(
            self.student.first_name,
            context_text,
        )
        self.assertNotIn(
            "responsible",
            context_text,
        )

    def test_invalid_period_is_rejected(
        self,
    ):
        response = self.create_insight(
            date_from=date(
                2026,
                11,
                4,
            ),
            date_to=date(
                2026,
                10,
                1,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unassigned_student_is_not_available(
        self,
    ):
        response = self.create_insight(
            student_id=(
                self.unassigned_student.id
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_use_other_professional_context(
        self,
    ):
        response = self.create_insight(
            user=self.teacher,
            context="PSICOLOGO",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # HU-24 / TASK-144

    def test_followup_suggestion_can_be_accepted(
        self,
    ):
        initial_followup_count = (
            AcademicFollowUp.objects.count()
        )

        response = self.create_insight(
            kind="FOLLOWUP_SUGGESTION",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            insight.review_status,
            AIInsight.ReviewStatus.PENDING,
        )

        review_response = (
            self.review_insight(
                insight,
                decision="ACCEPTED",
                notes=(
                    "La sugerencia es pertinente."
                ),
            )
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_200_OK,
        )

        insight.refresh_from_db()

        self.assertEqual(
            insight.review_status,
            AIInsight.ReviewStatus.ACCEPTED,
        )
        self.assertEqual(
            insight.reviewed_by,
            self.teacher,
        )
        self.assertIsNotNone(
            insight.reviewed_at
        )
        self.assertEqual(
            insight.professional_notes,
            "La sugerencia es pertinente.",
        )

        self.assertEqual(
            AcademicFollowUp.objects.count(),
            initial_followup_count,
        )

    def test_followup_suggestion_can_be_discarded_or_ignored(
        self,
    ):
        for decision in [
            "DISCARDED",
            "IGNORED",
        ]:
            with self.subTest(
                decision=decision
            ):
                response = self.create_insight(
                    kind=(
                        "FOLLOWUP_SUGGESTION"
                    ),
                )

                insight = AIInsight.objects.get(
                    pk=response.data["id"],
                )

                review_response = (
                    self.review_insight(
                        insight,
                        decision=decision,
                    )
                )

                self.assertEqual(
                    review_response.status_code,
                    status.HTTP_200_OK,
                )

                insight.refresh_from_db()

                self.assertEqual(
                    insight.review_status,
                    decision,
                )

    # HU-25 / TASK-150

    def test_intervention_recommendation_does_not_create_intervention(
        self,
    ):
        initial_count = (
            StudentIntervention
            .objects
            .count()
        )

        response = self.create_insight(
            kind=(
                "INTERVENTION_RECOMMENDATION"
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        review_response = self.review_insight(
            insight,
            decision="ACCEPTED",
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            StudentIntervention
            .objects
            .count(),
            initial_count,
        )

    def test_intervention_recommendation_can_be_discarded(
        self,
    ):
        response = self.create_insight(
            kind=(
                "INTERVENTION_RECOMMENDATION"
            ),
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        review_response = self.review_insight(
            insight,
            decision="DISCARDED",
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_200_OK,
        )

        insight.refresh_from_db()

        self.assertEqual(
            insight.review_status,
            AIInsight.ReviewStatus.DISCARDED,
        )

    # HU-26 / TASK-156

    def test_report_suggestion_uses_original_report_snapshot(
        self,
    ):
        response = self.create_insight(
            kind="REPORT_SUGGESTION",
            source_report_id=self.report.id,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            insight.source_report,
            self.report,
        )
        self.assertEqual(
            insight.student,
            self.report.student,
        )
        self.assertEqual(
            insight.date_from,
            self.report.date_from,
        )
        self.assertEqual(
            insight.date_to,
            self.report.date_to,
        )

        self.assertEqual(
            insight.context_snapshot[
                "source"
            ],
            "REPORT",
        )

        context_text = str(
            insight.context_snapshot
        )

        self.assertNotIn(
            self.student.institutional_code,
            context_text,
        )
        self.assertNotIn(
            self.student.first_name,
            context_text,
        )
        self.assertNotIn(
            "responsible",
            context_text,
        )

    def test_accepted_report_suggestion_does_not_modify_report(
        self,
    ):
        original_snapshot = deepcopy(
            self.report.content_snapshot
        )

        response = self.create_insight(
            kind="REPORT_SUGGESTION",
            source_report_id=self.report.id,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        edited_content = {
            "suggested_sections": [
                {
                    "section": (
                        "Observaciones"
                    ),
                    "draft_text": (
                        "Texto editado y "
                        "revisado por profesional."
                    ),
                    "rationale": (
                        "Apoyo de redacción."
                    ),
                }
            ],
        }

        review_response = self.review_insight(
            insight,
            decision="ACCEPTED",
            edited_content=edited_content,
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_200_OK,
        )

        insight.refresh_from_db()
        self.report.refresh_from_db()

        self.assertEqual(
            insight.edited_content,
            edited_content,
        )
        self.assertEqual(
            insight.review_status,
            AIInsight.ReviewStatus.ACCEPTED,
        )

        self.assertEqual(
            self.report.content_snapshot,
            original_snapshot,
        )

    def test_report_suggestion_can_be_discarded(
        self,
    ):
        response = self.create_insight(
            kind="REPORT_SUGGESTION",
            source_report_id=self.report.id,
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        review_response = self.review_insight(
            insight,
            decision="DISCARDED",
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_200_OK,
        )

        insight.refresh_from_db()

        self.assertEqual(
            insight.review_status,
            AIInsight.ReviewStatus.DISCARDED,
        )

    def test_user_cannot_use_another_users_report_for_ai(
        self,
    ):
        response = self.create_insight(
            user=self.teacher,
            context="DOCENTE",
            kind="REPORT_SUGGESTION",
            source_report_id=(
                self.other_report.id
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # HU-28 / TASK-168

    def test_list_is_private_to_creator_and_context(
        self,
    ):
        create_response = self.create_insight(
            kind="FOLLOWUP_SUGGESTION",
        )

        insight = AIInsight.objects.get(
            pk=create_response.data["id"],
        )

        self.client.force_authenticate(
            user=self.other_teacher,
        )

        list_response = self.client.get(
            reverse("ai-insight-list"),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            list_response.data["items"],
            [],
        )

        detail_response = self.client.get(
            reverse(
                "ai-insight-detail",
                kwargs={
                    "pk": insight.pk,
                },
            ),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_multirole_user_is_isolated_by_context(
        self,
    ):
        response = self.create_insight(
            user=self.multi_role_user,
            context="DOCENTE",
            kind="ANALYSIS",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        insight_id = response.data["id"]

        self.client.force_authenticate(
            user=self.multi_role_user,
        )

        teacher_response = self.client.get(
            reverse("ai-insight-list"),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            len(
                teacher_response
                .data["items"]
            ),
            1,
        )

        therapy_response = self.client.get(
            reverse("ai-insight-list"),
            {
                "context": "TERAPEUTA",
            },
        )

        self.assertEqual(
            therapy_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            therapy_response.data["items"],
            [],
        )

        detail_response = self.client.get(
            reverse(
                "ai-insight-detail",
                kwargs={
                    "pk": insight_id,
                },
            ),
            {
                "context": "TERAPEUTA",
            },
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_list_excludes_result_and_context_but_detail_includes_them(
        self,
    ):
        response = self.create_insight(
            kind="ANALYSIS",
        )

        insight_id = response.data["id"]

        self.client.force_authenticate(
            user=self.teacher,
        )

        list_response = self.client.get(
            reverse("ai-insight-list"),
            {
                "context": "DOCENTE",
            },
        )

        item = list_response.data["items"][0]

        self.assertNotIn(
            "result_json",
            item,
        )
        self.assertNotIn(
            "context_snapshot",
            item,
        )

        detail_response = self.client.get(
            reverse(
                "ai-insight-detail",
                kwargs={
                    "pk": insight_id,
                },
            ),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "result_json",
            detail_response.data,
        )
        self.assertIn(
            "context_snapshot",
            detail_response.data,
        )

    def test_analysis_cannot_be_accepted_or_discarded(
        self,
    ):
        response = self.create_insight(
            kind="ANALYSIS",
        )

        insight = AIInsight.objects.get(
            pk=response.data["id"],
        )

        review_response = self.review_insight(
            insight,
            decision="ACCEPTED",
        )

        self.assertEqual(
            review_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        insight.refresh_from_db()

        self.assertEqual(
            insight.review_status,
            (
                AIInsight
                .ReviewStatus
                .NOT_APPLICABLE
            ),
        )

    def test_filters_by_kind_review_status_and_source_report(
        self,
    ):
        suggestion_response = (
            self.create_insight(
                kind=(
                    "FOLLOWUP_SUGGESTION"
                ),
            )
        )

        suggestion = AIInsight.objects.get(
            pk=suggestion_response.data[
                "id"
            ],
        )

        self.review_insight(
            suggestion,
            decision="ACCEPTED",
        )

        self.create_insight(
            kind="ANALYSIS",
        )

        report_response = (
            self.create_insight(
                kind="REPORT_SUGGESTION",
                source_report_id=(
                    self.report.id
                ),
            )
        )

        self.client.force_authenticate(
            user=self.teacher,
        )

        accepted_response = self.client.get(
            reverse("ai-insight-list"),
            {
                "context": "DOCENTE",
                "kind": (
                    "FOLLOWUP_SUGGESTION"
                ),
                "review_status": (
                    "ACCEPTED"
                ),
            },
        )

        self.assertEqual(
            len(
                accepted_response
                .data["items"]
            ),
            1,
        )

        report_filter_response = (
            self.client.get(
                reverse(
                    "ai-insight-list"
                ),
                {
                    "context": "DOCENTE",
                    "source_report": (
                        self.report.id
                    ),
                },
            )
        )

        self.assertEqual(
            len(
                report_filter_response
                .data["items"]
            ),
            1,
        )
        self.assertEqual(
            report_filter_response
            .data["items"][0]["id"],
            report_response.data["id"],
        )

    def test_provider_failure_returns_service_unavailable(
        self,
    ):
        with patch(
            (
                "apps.ai_support.services."
                "get_ai_provider"
            )
        ) as provider_mock:
            provider = (
                provider_mock.return_value
            )

            provider.generate_structured.side_effect = (
                AIProviderError(
                    "Proveedor no disponible."
                )
            )

            response = self.create_insight(
                kind="ANALYSIS",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
