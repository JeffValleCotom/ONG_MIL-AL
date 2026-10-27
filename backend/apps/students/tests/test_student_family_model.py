from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.students.models import (
    Student,
    StudentFamilyMember,
)


class StudentFamilyMemberModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="family_model_user",
            password="test-password",
        )

        self.student = Student.objects.create(
            institutional_code="FAM-001",
            first_name="Ana",
            last_name="López",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

    def create_family_member(self, **overrides):
        data = {
            "student": self.student,
            "first_name": "María",
            "last_name": "López",
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
            "created_by": self.user,
            "updated_by": self.user,
        }
        data.update(overrides)

        return StudentFamilyMember.objects.create(**data)

    def test_family_member_can_be_created(self):
        family_member = self.create_family_member()

        self.assertEqual(
            family_member.student,
            self.student,
        )
        self.assertTrue(family_member.is_active)
        self.assertFalse(
            family_member.is_primary_contact
        )

    def test_only_one_active_primary_contact_per_student(self):
        self.create_family_member(
            is_primary_contact=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_family_member(
                    first_name="Carlos",
                    relationship=(
                        StudentFamilyMember.Relationship.PADRE
                    ),
                    is_primary_contact=True,
                )

    def test_active_family_member_requires_null_deactivated_at(
        self,
    ):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_family_member(
                    is_active=True,
                    deactivated_at=timezone.now(),
                )

    def test_inactive_family_member_requires_deactivated_at(
        self,
    ):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_family_member(
                    is_active=False,
                    deactivated_at=None,
                )

    def test_other_relationship_requires_detail(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_family_member(
                    relationship=(
                        StudentFamilyMember.Relationship.OTRO
                    ),
                    relationship_detail="",
                )

    def test_non_other_relationship_rejects_detail(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_family_member(
                    relationship=(
                        StudentFamilyMember.Relationship.MADRE
                    ),
                    relationship_detail="Madrina",
                )

    def test_inactive_primary_contact_does_not_block_new_primary(
        self,
    ):
        self.create_family_member(
            is_primary_contact=True,
            is_active=False,
            deactivated_at=timezone.now(),
        )

        new_primary = self.create_family_member(
            first_name="Carlos",
            relationship=(
                StudentFamilyMember.Relationship.PADRE
            ),
            is_primary_contact=True,
        )

        self.assertTrue(
            new_primary.is_primary_contact
        )
        self.assertTrue(new_primary.is_active)
