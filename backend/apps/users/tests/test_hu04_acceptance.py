from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class HU04AcceptanceTests(APITestCase):

    def setUp(self):
        self.administrator = User.objects.create_user(
            username="hu04_administrator",
            password="MilalAdmin123!",
        )
        self.administrator.groups.add(
            Group.objects.get(
                name="ADMINISTRADOR",
            )
        )

        self.docente = User.objects.create_user(
            username="hu04_docente",
            password="MilalDocente123!",
        )
        self.docente.groups.add(
            Group.objects.get(
                name="DOCENTE",
            )
        )

        self.target_user = User.objects.create_user(
            username="hu04_target",
            password="MilalTarget123!",
        )

    def test_administrator_can_access_user_management(self):
        self.client.force_login(
            self.administrator
        )

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_docente_cannot_access_user_management(self):
        self.client.force_login(
            self.docente
        )

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_administrator_can_access_role_management(self):
        self.client.force_login(
            self.administrator
        )

        response = self.client.get(
            reverse(
                "user-roles",
                kwargs={
                    "pk": self.target_user.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_docente_cannot_access_role_management(self):
        self.client.force_login(
            self.docente
        )

        response = self.client.get(
            reverse(
                "user-roles",
                kwargs={
                    "pk": self.target_user.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_multiple_roles_combine_group_permissions(self):
        multi_role_user = User.objects.create_user(
            username="hu04_multi_role",
            password="MilalMulti123!",
        )

        multi_role_user.groups.add(
            Group.objects.get(
                name="DOCENTE",
            ),
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL",
            ),
        )

        permissions = multi_role_user.get_group_permissions()

        self.assertIn(
            "users.manage_academic_followups",
            permissions,
        )
        self.assertIn(
            "users.manage_students",
            permissions,
        )
        self.assertIn(
            "users.view_dashboard",
            permissions,
        )

    def test_superuser_without_institutional_role_is_denied(self):
        technical_superuser = User.objects.create_superuser(
            username="hu04_superuser",
            password="MilalSuper123!",
        )

        self.client.force_login(
            technical_superuser
        )

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_inactive_administrator_is_denied(self):
        self.administrator.is_active = False
        self.administrator.save(
            update_fields=["is_active"]
        )

        self.client.force_login(
            self.administrator
        )

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
