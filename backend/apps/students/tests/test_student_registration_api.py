from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import Student


User = get_user_model()


class StudentRegistrationAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("student-list")

        self.responsible = User.objects.create_user(
            username="responsable_estudiantes",
            password="MilalStudent123!",
        )
        self.responsible.groups.add(
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            )
        )

        self.valid_payload = {
            "institutional_code": "MIL-001",
            "first_name": "Ana",
            "last_name": "López",
            "date_of_birth": "2015-05-10",
            "admission_date": "2024-01-15",
        }

    def authenticate_responsible(self):
        self.client.force_authenticate(
            user=self.responsible
        )

    def test_responsible_can_register_student(self):
        self.authenticate_responsible()

        payload = {
            **self.valid_payload,
            "institutional_code": "  mil-001  ",
            "first_name": "  Ana  ",
            "last_name": "  López  ",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        student = Student.objects.get()

        self.assertEqual(
            student.institutional_code,
            "MIL-001",
        )
        self.assertEqual(
            student.first_name,
            "Ana",
        )
        self.assertEqual(
            student.last_name,
            "López",
        )
        self.assertTrue(student.is_active)

        self.assertEqual(
            response.data["institutional_code"],
            "MIL-001",
        )
        self.assertTrue(response.data["is_active"])

    def test_duplicate_normalized_code_is_rejected(self):
        Student.objects.create(
            institutional_code="MIL-001",
            first_name="Primer",
            last_name="Estudiante",
            date_of_birth="2014-01-01",
            admission_date="2023-01-01",
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "institutional_code": "  mil-001  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "institutional_code",
            response.data,
        )
        self.assertEqual(
            Student.objects.count(),
            1,
        )

    def test_future_date_of_birth_is_rejected(self):
        self.authenticate_responsible()

        tomorrow = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "date_of_birth": tomorrow.isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "date_of_birth",
            response.data,
        )
        self.assertFalse(Student.objects.exists())

    def test_future_admission_date_is_rejected(self):
        self.authenticate_responsible()

        tomorrow = (
            timezone.localdate()
            + timedelta(days=1)
        )

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "admission_date": tomorrow.isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "admission_date",
            response.data,
        )
        self.assertFalse(Student.objects.exists())

    def test_admission_before_birth_is_rejected(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "date_of_birth": "2015-05-10",
                "admission_date": "2015-05-09",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "admission_date",
            response.data,
        )
        self.assertFalse(Student.objects.exists())

    def test_client_cannot_create_inactive_student(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        student = Student.objects.get()

        self.assertTrue(student.is_active)
        self.assertTrue(response.data["is_active"])

    def test_docente_cannot_register_student(self):
        docente = User.objects.create_user(
            username="docente_sin_gestion",
            password="MilalDocente123!",
        )
        docente.groups.add(
            Group.objects.get(name="DOCENTE")
        )

        self.client.force_authenticate(user=docente)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(Student.objects.exists())

    def test_psicologo_and_terapeuta_cannot_register_student(
        self,
    ):
        role_names = (
            "PSICOLOGO",
            "TERAPEUTA",
        )

        for role_name in role_names:
            with self.subTest(role=role_name):
                user = User.objects.create_user(
                    username=(
                        f"register_{role_name.lower()}"
                    ),
                    password="MilalNoManage123!",
                )
                user.groups.add(
                    Group.objects.get(
                        name=role_name
                    )
                )

                self.client.force_authenticate(
                    user=user
                )

                response = self.client.post(
                    self.url,
                    self.valid_payload,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertFalse(
                    Student.objects.exists()
                )

    def test_administrator_without_permission_cannot_register_student(
        self,
    ):
        administrator = User.objects.create_user(
            username="admin_sin_gestion_estudiantes",
            password="MilalAdmin123!",
        )
        administrator.groups.add(
            Group.objects.get(name="ADMINISTRADOR")
        )

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(Student.objects.exists())

    def test_anonymous_user_cannot_register_student(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
        self.assertFalse(Student.objects.exists())