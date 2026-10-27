from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentFamilyMember,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentFamilyQueryAPITests(APITestCase):
    def setUp(self):
        self.responsible = self.create_user_with_role(
            username="family_query_responsible",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.student = Student.objects.create(
            institutional_code="FAMILY-Q-001",
            first_name="Ana",
            last_name="Lopez",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

        self.other_student = Student.objects.create(
            institutional_code="FAMILY-Q-002",
            first_name="Luis",
            last_name="Perez",
            date_of_birth="2014-03-20",
            admission_date="2023-01-15",
        )

        self.family_url = reverse(
            "student-family-members",
            kwargs={
                "pk": self.student.pk,
            },
        )

    def create_user_with_role(
        self,
        *,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalFamilyQuery123!",
        )
        user.groups.add(
            Group.objects.get(
                name=role_name
            )
        )
        return user

    def assign_student(
        self,
        *,
        professional,
        professional_role,
        student=None,
    ):
        return StudentProfessionalAssignment.objects.create(
            student=student or self.student,
            professional=professional,
            professional_role=professional_role,
            assigned_by=self.responsible,
        )

    def create_family_member(
        self,
        *,
        student=None,
        creator=None,
        **overrides,
    ):
        student = student or self.student
        creator = creator or self.responsible

        data = {
            "student": student,
            "first_name": "Familiar",
            "last_name": "Prueba",
            "relationship": (
                StudentFamilyMember.Relationship.MADRE
            ),
            "relationship_detail": "",
            "phone": "",
            "email": "",
            "address": "",
            "is_primary_contact": False,
            "is_active": True,
            "deactivated_at": None,
            "created_by": creator,
            "updated_by": creator,
        }

        data.update(overrides)

        if (
            data["is_active"] is False
            and data["deactivated_at"] is None
        ):
            data["deactivated_at"] = timezone.now()

        return StudentFamilyMember.objects.create(
            **data
        )

    def record_url(self, student=None):
        student = student or self.student

        return reverse(
            "student-record",
            kwargs={
                "pk": student.pk,
            },
        )

    def test_responsible_can_query_family_members(self):
        family_member = self.create_family_member(
            first_name="Maria",
            last_name="Lopez",
            relationship=(
                StudentFamilyMember.Relationship.MADRE
            ),
            phone="+502 5555-1111",
            email="maria@example.com",
            address="Ciudad de Guatemala",
            is_primary_contact=True,
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        response = self.client.get(
            self.family_url,
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["items"]),
            1,
        )

        item = response.data["items"][0]

        self.assertEqual(
            item["id"],
            family_member.id,
        )
        self.assertEqual(
            item["student_id"],
            self.student.id,
        )
        self.assertEqual(
            item["first_name"],
            "Maria",
        )
        self.assertEqual(
            item["last_name"],
            "Lopez",
        )
        self.assertEqual(
            item["relationship"],
            "MADRE",
        )
        self.assertTrue(
            item["is_primary_contact"]
        )
        self.assertTrue(
            item["is_active"]
        )

    def test_family_query_does_not_mix_students(self):
        expected_member = self.create_family_member(
            first_name="Student",
            last_name="Family",
        )

        other_member = self.create_family_member(
            student=self.other_student,
            first_name="Other",
            last_name="Family",
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        response = self.client.get(
            self.family_url,
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = {
            item["id"]
            for item in response.data["items"]
        }

        self.assertEqual(
            returned_ids,
            {
                expected_member.id,
            },
        )
        self.assertNotIn(
            other_member.id,
            returned_ids,
        )

    def test_family_query_includes_active_and_inactive_history(
        self,
    ):
        inactive = self.create_family_member(
            first_name="Inactive",
            last_name="Alpha",
            is_active=False,
        )

        active_regular = self.create_family_member(
            first_name="Active",
            last_name="Beta",
        )

        active_primary = self.create_family_member(
            first_name="Primary",
            last_name="Zulu",
            is_primary_contact=True,
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        response = self.client.get(
            self.family_url,
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = [
            item["id"]
            for item in response.data["items"]
        ]

        self.assertEqual(
            returned_ids,
            [
                active_primary.id,
                active_regular.id,
                inactive.id,
            ],
        )

        inactive_item = next(
            item
            for item in response.data["items"]
            if item["id"] == inactive.id
        )

        self.assertFalse(
            inactive_item["is_active"]
        )
        self.assertIsNotNone(
            inactive_item["deactivated_at"]
        )

    def test_assigned_professionals_cannot_query_family_members(
        self,
    ):
        self.create_family_member(
            first_name="Private",
            last_name="Contact",
        )

        for role_name in (
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
        ):
            with self.subTest(
                role_name=role_name
            ):
                professional = self.create_user_with_role(
                    username=(
                        "family_query_"
                        f"{role_name.lower()}"
                    ),
                    role_name=role_name,
                )

                self.assign_student(
                    professional=professional,
                    professional_role=role_name,
                )

                self.client.force_authenticate(
                    user=professional
                )

                response = self.client.get(
                    self.family_url,
                    {
                        "context": role_name,
                    },
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_unassigned_professional_cannot_query_family(
        self,
    ):
        docente = self.create_user_with_role(
            username="family_query_unassigned",
            role_name="DOCENTE",
        )

        self.create_family_member()

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.family_url,
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_multi_role_family_query_respects_context(
        self,
    ):
        professional = User.objects.create_user(
            username="family_query_multirole",
            password="MilalFamilyQuery123!",
        )

        professional.groups.add(
            Group.objects.get(
                name="DOCENTE"
            ),
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            ),
        )

        self.assign_student(
            professional=professional,
            professional_role="DOCENTE",
            student=self.other_student,
        )

        self.create_family_member(
            student=self.other_student,
            first_name="Other",
            last_name="Contact",
        )

        self.client.force_authenticate(
            user=professional
        )

        docente_response = self.client.get(
            reverse(
                "student-family-members",
                kwargs={
                    "pk": self.other_student.pk,
                },
            ),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        responsible_response = self.client.get(
            reverse(
                "student-family-members",
                kwargs={
                    "pk": self.other_student.pk,
                },
            ),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            responsible_response.status_code,
            status.HTTP_200_OK,
        )

    def test_responsible_record_includes_family_section(
        self,
    ):
        family_member = self.create_family_member(
            first_name="Record",
            last_name="Contact",
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        response = self.client.get(
            self.record_url(),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "family",
            response.data["sections"],
        )

        family_items = (
            response.data["sections"]
            ["family"]
            ["items"]
        )

        self.assertEqual(
            [
                item["id"]
                for item in family_items
            ],
            [
                family_member.id,
            ],
        )

        self.assertTrue(
            response.data["capabilities"]
            ["manage_family"]
        )

    def test_assigned_professional_record_excludes_family(
        self,
    ):
        docente = self.create_user_with_role(
            username="family_record_docente",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
        )

        self.create_family_member(
            first_name="Private",
            last_name="Family",
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            self.record_url(),
            {
                "context": "DOCENTE",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "family",
            response.data["sections"],
        )

        self.assertFalse(
            response.data["capabilities"]
            ["manage_family"]
        )

    def test_family_endpoint_matches_record_family_section(
        self,
    ):
        self.create_family_member(
            first_name="First",
            last_name="Beta",
        )

        self.create_family_member(
            first_name="Primary",
            last_name="Zulu",
            is_primary_contact=True,
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        query_response = self.client.get(
            self.family_url,
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        record_response = self.client.get(
            self.record_url(),
            {
                "context": "RESPONSABLE_INSTITUCIONAL",
            },
        )

        self.assertEqual(
            query_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            record_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            query_response.data["items"],
            record_response.data["sections"]
            ["family"]
            ["items"],
        )
