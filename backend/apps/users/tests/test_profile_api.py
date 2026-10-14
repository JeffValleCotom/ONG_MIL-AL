from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class ProfileQueryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="perfil_docente",
            email="perfil.docente@test.com",
            first_name="Perfil",
            last_name="Docente",
            password="MilalProfile123!",
        )

        role = Group.objects.get(
            name="DOCENTE"
        )
        self.user.groups.add(role)

        self.profile_url = reverse(
            "user-profile"
        )

    def test_authenticated_user_can_view_own_profile(self):
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

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )

        self.assertEqual(
            response.data["first_name"],
            self.user.first_name,
        )

        self.assertEqual(
            response.data["last_name"],
            self.user.last_name,
        )

        self.assertEqual(
            response.data["roles"],
            ["DOCENTE"],
        )

    def test_profile_returns_current_authenticated_user(self):
        other_user = User.objects.create_user(
            username="otro_usuario",
            password="MilalOther123!",
        )

        self.client.force_login(self.user)

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotEqual(
            response.data["id"],
            other_user.id,
        )

        self.assertEqual(
            response.data["id"],
            self.user.id,
        )

    def test_unauthenticated_user_cannot_view_profile(self):
        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_update_own_profile(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            self.profile_url,
            {
                "email": "perfil.actualizado@test.com",
                "first_name": "Nombre actualizado",
                "last_name": "Apellido actualizado",
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
            "perfil.actualizado@test.com",
        )
        self.assertEqual(
            self.user.first_name,
            "Nombre actualizado",
        )
        self.assertEqual(
            self.user.last_name,
            "Apellido actualizado",
        )

    def test_profile_update_only_affects_authenticated_user(self):
        other_user = User.objects.create_user(
            username="otro_perfil",
            email="otro@test.com",
            first_name="Otro",
            last_name="Usuario",
            password="MilalOther123!",
        )

        self.client.force_login(self.user)

        response = self.client.patch(
            self.profile_url,
            {
                "first_name": "Actualizado",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()
        other_user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Actualizado",
        )
        self.assertEqual(
            other_user.first_name,
            "Otro",
        )

    def test_unauthenticated_user_cannot_update_profile(self):
        response = self.client.patch(
            self.profile_url,
            {
                "first_name": "No permitido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_profile_rejects_invalid_email(self):
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

    def test_profile_rejects_first_name_over_max_length(self):
        self.client.force_login(self.user)
        original_first_name = self.user.first_name

        response = self.client.patch(
            self.profile_url,
            {
                "first_name": "A" * 151,
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

    def test_profile_rejects_last_name_over_max_length(self):
        self.client.force_login(self.user)
        original_last_name = self.user.last_name

        response = self.client.patch(
            self.profile_url,
            {
                "last_name": "B" * 151,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.last_name,
            original_last_name,
        )

    def test_profile_trims_name_whitespace(self):
        self.client.force_login(self.user)

        response = self.client.patch(
            self.profile_url,
            {
                "first_name": "  Nombre  ",
                "last_name": "  Apellido  ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Nombre",
        )
        self.assertEqual(
            self.user.last_name,
            "Apellido",
        )
