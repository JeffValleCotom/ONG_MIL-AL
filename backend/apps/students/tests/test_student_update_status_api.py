from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import Student


User = get_user_model()


class StudentUpdateStatusAPITests(APITestCase):
    def setUp(self):
        self.responsible = User.objects.create_user(
            username="responsable_actualizacion",
            password="MilalStudentUpdate123!",
        )
        self.responsible.groups.add(
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            )
        )

        self.active_student = Student.objects.create(
            institutional_code="MIL-UPD-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2024-01-15",
            is_active=True,
        )

        self.inactive_student = Student.objects.create(
            institutional_code="MIL-UPD-002",
            first_name="Carlos",
            last_name="Pérez",
            date_of_birth="2014-08-20",
            admission_date="2023-02-01",
            is_active=False,
        )

    def authenticate_responsible(self):
        self.client.force_authenticate(
            user=self.responsible
        )

    def test_responsible_can_partially_update_student(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
                "institutional_code": "  mil-upd-010  ",
                "first_name": "  Ana María  ",
                "last_name": "  López Pérez  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.active_student.refresh_from_db()

        self.assertEqual(
            self.active_student.institutional_code,
            "MIL-UPD-010",
        )
        self.assertEqual(
            self.active_student.first_name,
            "Ana María",
        )
        self.assertEqual(
            self.active_student.last_name,
            "López Pérez",
        )
        self.assertTrue(
            self.active_student.is_active
        )

    def test_duplicate_normalized_code_is_rejected_on_update(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
                "institutional_code": "  mil-upd-002  ",
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

        self.active_student.refresh_from_db()

        self.assertEqual(
            self.active_student.institutional_code,
            "MIL-UPD-001",
        )

    def test_invalid_dates_are_rejected_on_update(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
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

    def test_is_active_cannot_be_changed_with_regular_patch(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "is_active",
            response.data,
        )

        self.active_student.refresh_from_db()

        self.assertTrue(
            self.active_student.is_active
        )

    def test_responsible_can_deactivate_student(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-deactivate",
                args=[self.active_student.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.active_student.refresh_from_db()

        self.assertFalse(
            self.active_student.is_active
        )
        self.assertFalse(
            response.data["student"]["is_active"]
        )

    def test_deactivating_inactive_student_is_idempotent(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-deactivate",
                args=[self.inactive_student.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.inactive_student.refresh_from_db()

        self.assertFalse(
            self.inactive_student.is_active
        )

    def test_responsible_can_activate_student(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-activate",
                args=[self.inactive_student.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.inactive_student.refresh_from_db()

        self.assertTrue(
            self.inactive_student.is_active
        )
        self.assertTrue(
            response.data["student"]["is_active"]
        )

    def test_activating_active_student_is_idempotent(self):
        self.authenticate_responsible()

        response = self.client.patch(
            reverse(
                "student-activate",
                args=[self.active_student.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.active_student.refresh_from_db()

        self.assertTrue(
            self.active_student.is_active
        )

    def test_roles_without_manage_students_cannot_modify_student(self):
        role_names = (
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
            "ADMINISTRADOR",
        )

        for role_name in role_names:
            with self.subTest(role=role_name):
                user = User.objects.create_user(
                    username=(
                        f"update_{role_name.lower()}"
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

                update_response = self.client.patch(
                    reverse(
                        "student-detail",
                        args=[self.active_student.pk],
                    ),
                    {
                        "first_name": "Modificado",
                    },
                    format="json",
                )

                status_response = self.client.patch(
                    reverse(
                        "student-deactivate",
                        args=[self.active_student.pk],
                    ),
                    {},
                    format="json",
                )

                self.assertEqual(
                    update_response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    status_response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

        self.active_student.refresh_from_db()

        self.assertEqual(
            self.active_student.first_name,
            "Ana",
        )
        self.assertTrue(
            self.active_student.is_active
        )

    def test_anonymous_user_cannot_modify_student(self):
        response = self.client.patch(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
                "first_name": "Modificado",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

        self.active_student.refresh_from_db()

        self.assertEqual(
            self.active_student.first_name,
            "Ana",
        )

    def test_delete_student_is_not_allowed(self):
        self.authenticate_responsible()

        response = self.client.delete(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            Student.objects.filter(
                pk=self.active_student.pk
            ).exists()
        )

    def test_put_student_is_not_allowed(self):
        self.authenticate_responsible()

        response = self.client.put(
            reverse(
                "student-detail",
                args=[self.active_student.pk],
            ),
            {
                "institutional_code": "MIL-PUT-001",
                "first_name": "Nombre",
                "last_name": "Completo",
                "date_of_birth": "2015-01-01",
                "admission_date": "2024-01-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
