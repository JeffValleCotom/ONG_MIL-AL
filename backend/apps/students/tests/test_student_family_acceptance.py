from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentFamilyMember,
    StudentProfessionalAssignment,
)


User = get_user_model()


class StudentFamilyAcceptanceTests(APITestCase):
    def setUp(self):
        self.responsible = User.objects.create_user(
            username="family_acceptance_responsible",
            password="MilalFamilyAcceptance123!",
        )

        self.responsible.groups.add(
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            )
        )

        self.student = Student.objects.create(
            institutional_code="FAMILY-A-001",
            first_name="Ana",
            last_name="Lopez",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

        self.client.force_authenticate(
            user=self.responsible
        )

    def family_url(self):
        return reverse(
            "student-family-members",
            kwargs={
                "pk": self.student.pk,
            },
        )

    def update_url(self, family_member_id):
        return reverse(
            "student-family-member-detail",
            kwargs={
                "pk": self.student.pk,
                "family_member_id": family_member_id,
            },
        )

    def deactivate_url(self, family_member_id):
        return reverse(
            "student-deactivate-family-member",
            kwargs={
                "pk": self.student.pk,
                "family_member_id": family_member_id,
            },
        )

    def record_url(self):
        return reverse(
            "student-record",
            kwargs={
                "pk": self.student.pk,
            },
        )

    def test_family_information_complete_lifecycle(
        self,
    ):
        create_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Maria",
                "last_name": "Lopez",
                "relationship": "MADRE",
                "relationship_detail": "",
                "phone": "+502 5555-1000",
                "email": "maria@example.com",
                "address": "Guatemala",
                "is_primary_contact": False,
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        family_member_id = create_response.data["id"]

        query_response = self.client.get(
            self.family_url(),
        )

        self.assertEqual(
            query_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(query_response.data["items"]),
            1,
        )
        self.assertEqual(
            query_response.data["items"][0]["phone"],
            "+502 5555-1000",
        )

        update_response = self.client.patch(
            self.update_url(family_member_id),
            {
                "phone": "+502 5555-2000",
                "address": "Ciudad de Guatemala",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )

        final_query_response = self.client.get(
            self.family_url(),
        )

        self.assertEqual(
            final_query_response.status_code,
            status.HTTP_200_OK,
        )

        family_data = (
            final_query_response.data["items"][0]
        )

        self.assertEqual(
            family_data["phone"],
            "+502 5555-2000",
        )
        self.assertEqual(
            family_data["address"],
            "Ciudad de Guatemala",
        )

        family_member = (
            StudentFamilyMember.objects.get(
                pk=family_member_id
            )
        )

        self.assertEqual(
            family_member.created_by,
            self.responsible,
        )
        self.assertEqual(
            family_member.updated_by,
            self.responsible,
        )

    def test_primary_contact_can_be_replaced_after_deactivation(
        self,
    ):
        first_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Maria",
                "last_name": "Lopez",
                "relationship": "MADRE",
                "relationship_detail": "",
                "phone": "",
                "email": "",
                "address": "",
                "is_primary_contact": True,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        first_id = first_response.data["id"]

        deactivate_response = self.client.patch(
            self.deactivate_url(first_id),
            {},
            format="json",
        )

        self.assertEqual(
            deactivate_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Carlos",
                "last_name": "Lopez",
                "relationship": "PADRE",
                "relationship_detail": "",
                "phone": "",
                "email": "",
                "address": "",
                "is_primary_contact": True,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        query_response = self.client.get(
            self.family_url(),
        )

        self.assertEqual(
            query_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(query_response.data["items"]),
            2,
        )

        first_member = (
            StudentFamilyMember.objects.get(
                pk=first_id
            )
        )

        second_member = (
            StudentFamilyMember.objects.get(
                pk=second_response.data["id"]
            )
        )

        self.assertFalse(
            first_member.is_active
        )
        self.assertFalse(
            first_member.is_primary_contact
        )
        self.assertIsNotNone(
            first_member.deactivated_at
        )

        self.assertTrue(
            second_member.is_active
        )
        self.assertTrue(
            second_member.is_primary_contact
        )

        self.assertEqual(
            StudentFamilyMember.objects.filter(
                student=self.student,
                is_active=True,
                is_primary_contact=True,
            ).count(),
            1,
        )

    def test_record_family_section_matches_family_endpoint(
        self,
    ):
        first_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Maria",
                "last_name": "Lopez",
                "relationship": "MADRE",
                "relationship_detail": "",
                "phone": "+502 5555-3000",
                "email": "",
                "address": "",
                "is_primary_contact": True,
            },
            format="json",
        )

        second_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Carlos",
                "last_name": "Lopez",
                "relationship": "PADRE",
                "relationship_detail": "",
                "phone": "",
                "email": "",
                "address": "",
                "is_primary_contact": False,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.patch(
            self.update_url(
                second_response.data["id"]
            ),
            {
                "phone": "+502 5555-4000",
            },
            format="json",
        )

        self.client.patch(
            self.deactivate_url(
                first_response.data["id"]
            ),
            {},
            format="json",
        )

        endpoint_response = self.client.get(
            self.family_url(),
        )

        record_response = self.client.get(
            self.record_url(),
        )

        self.assertEqual(
            endpoint_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            record_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "family",
            record_response.data["sections"],
        )

        self.assertEqual(
            endpoint_response.data["items"],
            record_response.data[
                "sections"
            ]["family"]["items"],
        )

    def test_family_information_remains_private_from_assigned_professional(
        self,
    ):
        create_response = self.client.post(
            self.family_url(),
            {
                "first_name": "Maria",
                "last_name": "Lopez",
                "relationship": "MADRE",
                "relationship_detail": "",
                "phone": "+502 5555-5000",
                "email": "maria@example.com",
                "address": "Guatemala",
                "is_primary_contact": True,
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        responsible_family_response = (
            self.client.get(
                self.family_url(),
            )
        )

        responsible_record_response = (
            self.client.get(
                self.record_url(),
            )
        )

        self.assertEqual(
            responsible_family_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn(
            "family",
            responsible_record_response.data[
                "sections"
            ],
        )
        self.assertTrue(
            responsible_record_response.data[
                "capabilities"
            ]["manage_family"]
        )

        docente = User.objects.create_user(
            username="family_acceptance_docente",
            password="MilalFamilyAcceptance123!",
        )

        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        self.client.force_authenticate(
            user=docente
        )

        docente_family_response = self.client.get(
            f"{self.family_url()}?context=DOCENTE"
        )

        self.assertEqual(
            docente_family_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        docente_record_response = self.client.get(
            f"{self.record_url()}?context=DOCENTE"
        )

        self.assertEqual(
            docente_record_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "family",
            docente_record_response.data[
                "sections"
            ],
        )

        self.assertFalse(
            docente_record_response.data[
                "capabilities"
            ]["manage_family"]
        )
