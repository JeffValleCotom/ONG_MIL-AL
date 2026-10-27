from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentFamilyMember,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentFamilyRegistrationAPITests(APITestCase):
    def setUp(self):
        self.responsible = self.create_user_with_role(
            username="family_responsible",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.student = Student.objects.create(
            institutional_code="FAMILY-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

        self.url = reverse(
            "student-family-members",
            kwargs={
                "pk": self.student.pk,
            },
        )

        self.valid_payload = {
            "first_name": "María",
            "last_name": "López",
            "relationship": "MADRE",
            "relationship_detail": "",
            "phone": "+502 5555-1111",
            "email": "maria@example.com",
            "address": "Ciudad de Guatemala",
            "is_primary_contact": True,
        }

    def create_user_with_role(
        self,
        *,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalFamily123!",
        )
        user.groups.add(
            Group.objects.get(
                name=role_name
            )
        )
        return user

    def authenticate_responsible(self):
        self.client.force_authenticate(
            user=self.responsible
        )

    def create_family_member(
        self,
        **overrides,
    ):
        data = {
            "student": self.student,
            "first_name": "Existing",
            "last_name": "Contact",
            "relationship": (
                StudentFamilyMember.Relationship.PADRE
            ),
            "relationship_detail": "",
            "phone": "",
            "email": "",
            "address": "",
            "is_primary_contact": False,
            "is_active": True,
            "deactivated_at": None,
            "created_by": self.responsible,
            "updated_by": self.responsible,
        }
        data.update(overrides)

        return StudentFamilyMember.objects.create(
            **data
        )

    def test_responsible_can_register_family_member(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "first_name": "  María  ",
                "last_name": "  López  ",
                "phone": "  +502 5555-1111  ",
                "address": "  Ciudad de Guatemala  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        family_member = StudentFamilyMember.objects.get()

        self.assertEqual(
            family_member.student,
            self.student,
        )
        self.assertEqual(
            family_member.first_name,
            "María",
        )
        self.assertEqual(
            family_member.last_name,
            "López",
        )
        self.assertEqual(
            family_member.phone,
            "+502 5555-1111",
        )
        self.assertEqual(
            family_member.address,
            "Ciudad de Guatemala",
        )
        self.assertTrue(
            family_member.is_primary_contact
        )
        self.assertTrue(family_member.is_active)
        self.assertIsNone(
            family_member.deactivated_at
        )
        self.assertEqual(
            family_member.created_by,
            self.responsible,
        )
        self.assertEqual(
            family_member.updated_by,
            self.responsible,
        )

        self.assertEqual(
            response.data["student_id"],
            self.student.id,
        )

    def test_student_from_url_cannot_be_overridden(
        self,
    ):
        other_student = Student.objects.create(
            institutional_code="FAMILY-002",
            first_name="Luis",
            last_name="Pérez",
            date_of_birth="2014-03-20",
            admission_date="2023-01-15",
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "student_id": other_student.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        family_member = StudentFamilyMember.objects.get()

        self.assertEqual(
            family_member.student,
            self.student,
        )
        self.assertEqual(
            response.data["student_id"],
            self.student.id,
        )

    def test_other_relationship_requires_detail(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "relationship": "OTRO",
                "relationship_detail": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "relationship_detail",
            response.data,
        )
        self.assertFalse(
            StudentFamilyMember.objects.exists()
        )

    def test_non_other_relationship_rejects_detail(
        self,
    ):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "relationship": "MADRE",
                "relationship_detail": "Madrina",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "relationship_detail",
            response.data,
        )

    def test_invalid_relationship_is_rejected(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "relationship": "DESCONOCIDO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "relationship",
            response.data,
        )

    def test_invalid_email_is_rejected(self):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "email": "correo-invalido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "email",
            response.data,
        )

    def test_second_active_primary_contact_is_rejected(
        self,
    ):
        self.create_family_member(
            is_primary_contact=True,
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "is_primary_contact",
            response.data,
        )
        self.assertEqual(
            StudentFamilyMember.objects.count(),
            1,
        )

    def test_client_cannot_control_family_status(
        self,
    ):
        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            {
                **self.valid_payload,
                "is_active": False,
                "deactivated_at": (
                    "2026-01-01T12:00:00Z"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        family_member = StudentFamilyMember.objects.get()

        self.assertTrue(family_member.is_active)
        self.assertIsNone(
            family_member.deactivated_at
        )

    def test_docente_cannot_register_family_member(
        self,
    ):
        docente = self.create_user_with_role(
            username="family_docente",
            role_name="DOCENTE",
        )

        self.client.force_authenticate(
            user=docente
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
            StudentFamilyMember.objects.exists()
        )

    def test_psychologist_and_therapist_cannot_register(
        self,
    ):
        for role_name in (
            "PSICOLOGO",
            "TERAPEUTA",
        ):
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=(
                        f"family_{role_name.lower()}"
                    ),
                    role_name=role_name,
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
            StudentFamilyMember.objects.exists()
        )

    def test_responsible_without_manage_students_cannot_register(
        self,
    ):
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

        self.authenticate_responsible()

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
            StudentFamilyMember.objects.exists()
        )

    def test_multi_role_registration_respects_context(
        self,
    ):
        user = self.create_user_with_role(
            username="family_multi_role",
            role_name="DOCENTE",
        )
        user.groups.add(
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=user,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        self.client.force_authenticate(
            user=user
        )

        docente_response = self.client.post(
            (
                f"{self.url}"
                "?context=DOCENTE"
            ),
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            StudentFamilyMember.objects.exists()
        )

        responsible_response = self.client.post(
            (
                f"{self.url}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            responsible_response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            StudentFamilyMember.objects.count(),
            1,
        )

    def test_family_member_can_be_registered_for_inactive_student(
        self,
    ):
        self.student.is_active = False
        self.student.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        self.authenticate_responsible()

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            StudentFamilyMember.objects.count(),
            1,
        )

    def test_nonexistent_student_returns_not_found(
        self,
    ):
        self.authenticate_responsible()

        url = reverse(
            "student-family-members",
            kwargs={
                "pk": 999999,
            },
        )

        response = self.client.post(
            url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertFalse(
            StudentFamilyMember.objects.exists()
        )
