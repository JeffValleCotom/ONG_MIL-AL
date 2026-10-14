from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class HU03ProfileAcceptanceTests(APITestCase):

    def setUp(self):
        self.profile_url = reverse("user-profile")

        self.user = User.objects.create_user(
            username="perfil_usuario",
            email="perfil@test.com",
            first_name="Nombre",
            last_name="Apellido",
            password="MilalProfile123!",
        )

        docente_role = Group.objects.get(
            name="DOCENTE"
        )

        self.user.groups.add(docente_role)

    def test_authenticated_user_can_consult_own_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            self.user.id,
        )
        self.assertEqual(
            response.data["username"],
            self.user.username,
        )
        self.assertIn(
            "DOCENTE",
            response.data["roles"],
        )

    def test_authenticated_user_can_update_allowed_profile_data(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            self.profile_url,
            {
                "email": "nuevo@test.com",
                "first_name": "  Nuevo Nombre  ",
                "last_name": "  Nuevo Apellido  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "nuevo@test.com",
        )
        self.assertEqual(
            self.user.first_name,
            "Nuevo Nombre",
        )
        self.assertEqual(
            self.user.last_name,
            "Nuevo Apellido",
        )

    def test_invalid_profile_data_is_rejected(self):
        self.client.force_login(self.user)

        original_email = self.user.email

        response = self.client.patch(
            self.profile_url,
            {
                "email": "correo-invalido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            original_email,
        )

    def test_restricted_profile_data_cannot_be_modified(self):
        self.client.force_login(self.user)

        original_username = self.user.username

        response = self.client.patch(
            self.profile_url,
            {
                "username": "usuario_alterado",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.username,
            original_username,
        )

    def test_restricted_field_invalidates_complete_update(self):
        self.client.force_login(self.user)

        original_first_name = self.user.first_name
        original_username = self.user.username

        response = self.client.patch(
            self.profile_url,
            {
                "first_name": "Nombre nuevo",
                "username": "usuario_no_permitido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            original_first_name,
        )
        self.assertEqual(
            self.user.username,
            original_username,
        )

    def test_unauthenticated_user_cannot_manage_profile(self):
        get_response = self.client.get(
            self.profile_url
        )

        patch_response = self.client.patch(
            self.profile_url,
            {
                "first_name": "No permitido",
            },
            format="json",
        )

        self.assertEqual(
            get_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            patch_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )