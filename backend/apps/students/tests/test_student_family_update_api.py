from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
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


class StudentFamilyUpdateAPITests(APITestCase):
    def setUp(self):
        self.responsible = self.create_user_with_role(
            username="family_update_responsible",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        self.student = Student.objects.create(
            institutional_code="FAMILY-U-001",
            first_name="Ana",
            last_name="Lopez",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

        self.other_student = Student.objects.create(
            institutional_code="FAMILY-U-002",
            first_name="Luis",
            last_name="Perez",
            date_of_birth="2014-03-20",
            admission_date="2023-01-15",
        )

    def create_user_with_role(
        self,
        *,
        username,
        role_name,
    ):
        user = User.objects.create_user(
            username=username,
            password="MilalFamilyUpdate123!",
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
            "first_name": "Family",
            "last_name": "Member",
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

        return StudentFamilyMember.objects.create(
            **data
        )

    def update_url(
        self,
        family_member,
        student=None,
    ):
        return reverse(
            "student-family-member-detail",
            kwargs={
                "pk": (
                    student or self.student
                ).pk,
                "family_member_id": family_member.pk,
            },
        )

    def deactivate_url(
        self,
        family_member,
        student=None,
    ):
        return reverse(
            "student-deactivate-family-member",
            kwargs={
                "pk": (
                    student or self.student
                ).pk,
                "family_member_id": family_member.pk,
            },
        )

    def authenticate_responsible(self):
        self.client.force_authenticate(
            user=self.responsible
        )

    def test_responsible_can_partially_update_family_member(
        self,
    ):
        original_creator = self.create_user_with_role(
            username="family_original_creator",
            role_name="RESPONSABLE_INSTITUCIONAL",
        )

        family_member = self.create_family_member(
            creator=original_creator,
            first_name="Maria",
            last_name="Lopez",
            phone="+502 1111-1111",
            email="old@example.com",
            address="Guatemala",
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "phone": "  +502 5555-2222  ",
                "email": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.first_name,
            "Maria",
        )
        self.assertEqual(
            family_member.last_name,
            "Lopez",
        )
        self.assertEqual(
            family_member.phone,
            "+502 5555-2222",
        )
        self.assertEqual(
            family_member.email,
            "new@example.com",
        )
        self.assertEqual(
            family_member.address,
            "Guatemala",
        )
        self.assertEqual(
            family_member.created_by,
            original_creator,
        )
        self.assertEqual(
            family_member.updated_by,
            self.responsible,
        )

    def test_update_cannot_move_family_member_to_other_student(
        self,
    ):
        family_member = self.create_family_member()

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "student_id": self.other_student.id,
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.student,
            self.student,
        )
        self.assertEqual(
            family_member.first_name,
            "Updated",
        )

    def test_changing_other_relationship_clears_detail(
        self,
    ):
        family_member = self.create_family_member(
            relationship=(
                StudentFamilyMember.Relationship.OTRO
            ),
            relationship_detail="Encargado legal",
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "relationship": "PADRE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.relationship,
            StudentFamilyMember.Relationship.PADRE,
        )
        self.assertEqual(
            family_member.relationship_detail,
            "",
        )

    def test_update_to_other_relationship_requires_detail(
        self,
    ):
        family_member = self.create_family_member()

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "relationship": "OTRO",
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

    def test_second_active_primary_contact_is_rejected(
        self,
    ):
        self.create_family_member(
            first_name="Primary",
            is_primary_contact=True,
        )

        family_member = self.create_family_member(
            first_name="Secondary",
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "is_primary_contact": True,
            },
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

        family_member.refresh_from_db()

        self.assertFalse(
            family_member.is_primary_contact
        )

    def test_existing_primary_contact_can_update_its_data(
        self,
    ):
        family_member = self.create_family_member(
            first_name="Primary",
            is_primary_contact=True,
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "phone": "+502 4444-4444",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertTrue(
            family_member.is_primary_contact
        )
        self.assertEqual(
            family_member.phone,
            "+502 4444-4444",
        )

    def test_inactive_family_member_can_be_corrected_but_not_primary(
        self,
    ):
        family_member = self.create_family_member(
            first_name="Historic",
            is_active=False,
            deactivated_at=timezone.now(),
        )

        self.authenticate_responsible()

        correction_response = self.client.patch(
            self.update_url(family_member),
            {
                "last_name": "Corrected",
            },
            format="json",
        )

        self.assertEqual(
            correction_response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.last_name,
            "Corrected",
        )
        self.assertFalse(
            family_member.is_active
        )

        primary_response = self.client.patch(
            self.update_url(family_member),
            {
                "is_primary_contact": True,
            },
            format="json",
        )

        self.assertEqual(
            primary_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "is_primary_contact",
            primary_response.data,
        )

    def test_family_member_from_other_student_cannot_be_updated(
        self,
    ):
        other_member = self.create_family_member(
            student=self.other_student,
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(other_member),
            {
                "first_name": "Forbidden",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        other_member.refresh_from_db()

        self.assertEqual(
            other_member.first_name,
            "Family",
        )

    def test_assigned_docente_cannot_update_family_member(
        self,
    ):
        docente = self.create_user_with_role(
            username="family_update_docente",
            role_name="DOCENTE",
        )

        self.assign_student(
            professional=docente,
            professional_role="DOCENTE",
        )

        family_member = self.create_family_member()

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.patch(
            (
                f"{self.update_url(family_member)}"
                "?context=DOCENTE"
            ),
            {
                "first_name": "Forbidden",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_multi_role_update_respects_active_context(
        self,
    ):
        professional = User.objects.create_user(
            username="family_update_multirole",
            password="MilalFamilyUpdate123!",
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
        )

        family_member = self.create_family_member()

        self.client.force_authenticate(
            user=professional
        )

        docente_response = self.client.patch(
            (
                f"{self.update_url(family_member)}"
                "?context=DOCENTE"
            ),
            {
                "first_name": "DocenteAttempt",
            },
            format="json",
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        responsible_response = self.client.patch(
            (
                f"{self.update_url(family_member)}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "first_name": "ResponsibleUpdate",
            },
            format="json",
        )

        self.assertEqual(
            responsible_response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.first_name,
            "ResponsibleUpdate",
        )

    def test_responsible_without_manage_students_cannot_update(
        self,
    ):
        family_member = self.create_family_member()

        responsible_group = Group.objects.get(
            name="RESPONSABLE_INSTITUCIONAL"
        )

        responsible_group.permissions.remove(
            Permission.objects.get(
                codename="manage_students"
            )
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.update_url(family_member),
            {
                "first_name": "Forbidden",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_deactivate_family_member_preserves_history(
        self,
    ):
        family_member = self.create_family_member(
            first_name="Primary",
            is_primary_contact=True,
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.deactivate_url(family_member),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertFalse(
            family_member.is_active
        )
        self.assertFalse(
            family_member.is_primary_contact
        )
        self.assertIsNotNone(
            family_member.deactivated_at
        )
        self.assertEqual(
            family_member.updated_by,
            self.responsible,
        )

        self.assertTrue(
            StudentFamilyMember.objects.filter(
                pk=family_member.pk
            ).exists()
        )

    def test_deactivation_is_idempotent(
        self,
    ):
        family_member = self.create_family_member()

        self.authenticate_responsible()

        first_response = self.client.patch(
            self.deactivate_url(family_member),
            {},
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()
        first_deactivated_at = (
            family_member.deactivated_at
        )

        second_response = self.client.patch(
            self.deactivate_url(family_member),
            {},
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        family_member.refresh_from_db()

        self.assertEqual(
            family_member.deactivated_at,
            first_deactivated_at,
        )

        self.assertEqual(
            StudentFamilyMember.objects.filter(
                pk=family_member.pk
            ).count(),
            1,
        )

    def test_other_students_family_member_cannot_be_deactivated(
        self,
    ):
        other_member = self.create_family_member(
            student=self.other_student,
        )

        self.authenticate_responsible()

        response = self.client.patch(
            self.deactivate_url(other_member),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        other_member.refresh_from_db()

        self.assertTrue(
            other_member.is_active
        )