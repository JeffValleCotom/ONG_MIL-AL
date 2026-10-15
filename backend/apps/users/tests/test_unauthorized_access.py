from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UnauthorizedAccessTests(APITestCase):

    def setUp(self):
        self.operator = User.objects.create_user(
            username="unauthorized_operator",
            password="MilalUnauthorized123!",
        )

        docente = Group.objects.get(
            name="DOCENTE",
        )
        self.operator.groups.add(
            docente,
        )

        self.target_user = User.objects.create_user(
            username="protected_user",
            email="protected@test.com",
            first_name="Nombre",
            last_name="Protegido",
            password="MilalProtected123!",
        )

        self.client.force_login(
            self.operator
        )

    def test_user_without_manage_users_cannot_create_user(self):
        users_before = User.objects.count()

        response = self.client.post(
            reverse("user-list"),
            {
                "username": "unauthorized_created",
                "email": "created@test.com",
                "first_name": "No",
                "last_name": "Permitido",
                "password": "MilalCreated123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            User.objects.count(),
            users_before,
        )

        self.assertFalse(
            User.objects.filter(
                username="unauthorized_created",
            ).exists()
        )

    def test_user_without_manage_users_cannot_update_user(self):
        original_email = self.target_user.email
        original_first_name = self.target_user.first_name

        response = self.client.patch(
            reverse(
                "user-detail",
                kwargs={
                    "pk": self.target_user.pk,
                },
            ),
            {
                "email": "altered@test.com",
                "first_name": "Alterado",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.target_user.refresh_from_db()

        self.assertEqual(
            self.target_user.email,
            original_email,
        )
        self.assertEqual(
            self.target_user.first_name,
            original_first_name,
        )

    def test_user_without_manage_users_cannot_deactivate_user(self):
        self.assertTrue(
            self.target_user.is_active
        )

        response = self.client.patch(
            reverse(
                "user-deactivate",
                kwargs={
                    "pk": self.target_user.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.target_user.refresh_from_db()

        self.assertTrue(
            self.target_user.is_active
        )

    def test_user_without_manage_users_cannot_activate_user(self):
        self.target_user.is_active = False
        self.target_user.save(
            update_fields=["is_active"]
        )

        response = self.client.patch(
            reverse(
                "user-activate",
                kwargs={
                    "pk": self.target_user.pk,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.target_user.refresh_from_db()

        self.assertFalse(
            self.target_user.is_active
        )

    def test_user_without_manage_roles_cannot_change_roles(self):
        original_roles = set(
            self.target_user.groups.values_list(
                "name",
                flat=True,
            )
        )

        response = self.client.patch(
            reverse(
                "user-roles",
                kwargs={
                    "pk": self.target_user.pk,
                },
            ),
            {
                "roles": [
                    "ADMINISTRADOR",
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.target_user.refresh_from_db()

        current_roles = set(
            self.target_user.groups.values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            current_roles,
            original_roles,
        )
