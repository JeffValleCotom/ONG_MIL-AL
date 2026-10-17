from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import Student


User = get_user_model()


class StudentQueryAPITests(APITestCase):
    VIEW_ROLES = (
        "DOCENTE",
        "PSICOLOGO",
        "TERAPEUTA",
        "RESPONSABLE_INSTITUCIONAL",
    )

    def setUp(self):
        self.student_ana = Student.objects.create(
            institutional_code="MIL-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2024-01-15",
            is_active=True,
        )

        self.student_carlos = Student.objects.create(
            institutional_code="MIL-002",
            first_name="Carlos",
            last_name="Pérez",
            date_of_birth="2014-08-20",
            admission_date="2023-02-01",
            is_active=False,
        )

        self.student_maria = Student.objects.create(
            institutional_code="ABC-100",
            first_name="María",
            last_name="López",
            date_of_birth="2016-03-12",
            admission_date="2025-01-10",
            is_active=True,
        )

        self.list_url = reverse("student-list")

    def create_user_with_role(
        self,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalStudentQuery123!",
        )
        user.groups.add(
            Group.objects.get(name=role_name)
        )

        return user

    def authenticate_with_role(
        self,
        username,
        role_name,
    ):
        user = self.create_user_with_role(
            username=username,
            role_name=role_name,
        )

        self.client.force_authenticate(user=user)

        return user

    def test_roles_with_view_students_can_list_students(self):
        for role_name in self.VIEW_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"query_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                response = self.client.get(
                    self.list_url
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )
                self.assertEqual(
                    len(response.data),
                    3,
                )

    def test_user_with_view_students_can_retrieve_student(self):
        self.authenticate_with_role(
            username="docente_detalle",
            role_name="DOCENTE",
        )

        response = self.client.get(
            reverse(
                "student-detail",
                args=[self.student_ana.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["institutional_code"],
            "MIL-001",
        )
        self.assertEqual(
            response.data["first_name"],
            "Ana",
        )

    def test_search_by_institutional_code(self):
        self.authenticate_with_role(
            username="docente_codigo",
            role_name="DOCENTE",
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "mil-002",
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
            response.data[0]["institutional_code"],
            "MIL-002",
        )

    def test_search_by_first_name(self):
        self.authenticate_with_role(
            username="psicologo_nombre",
            role_name="PSICOLOGO",
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "ana",
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
            response.data[0]["first_name"],
            "Ana",
        )

    def test_search_by_last_name(self):
        self.authenticate_with_role(
            username="terapeuta_apellido",
            role_name="TERAPEUTA",
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "lópez",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            2,
        )

        codes = {
            student["institutional_code"]
            for student in response.data
        }

        self.assertEqual(
            codes,
            {
                "MIL-001",
                "ABC-100",
            },
        )

    def test_filter_active_students(self):
        self.authenticate_with_role(
            username="responsable_activos",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        response = self.client.get(
            self.list_url,
            {
                "status": "active",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                student["is_active"]
                for student in response.data
            )
        )

    def test_filter_inactive_students(self):
        self.authenticate_with_role(
            username="responsable_inactivos",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        response = self.client.get(
            self.list_url,
            {
                "status": "inactive",
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
            response.data[0]["institutional_code"],
            "MIL-002",
        )
        self.assertFalse(
            response.data[0]["is_active"]
        )

    def test_search_and_status_filter_can_be_combined(self):
        self.authenticate_with_role(
            username="docente_combinado",
            role_name="DOCENTE",
        )

        response = self.client.get(
            self.list_url,
            {
                "search": "lópez",
                "status": "active",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                student["is_active"]
                for student in response.data
            )
        )

    def test_invalid_status_filter_is_rejected(self):
        self.authenticate_with_role(
            username="docente_estado_invalido",
            role_name="DOCENTE",
        )

        response = self.client.get(
            self.list_url,
            {
                "status": "deleted",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "status",
            response.data,
        )

    def test_administrator_without_view_students_cannot_list(self):
        self.authenticate_with_role(
            username="administrador_sin_consulta",
            role_name="ADMINISTRADOR",
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_anonymous_user_cannot_list_students(self):
        response = self.client.get(
            self.list_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
