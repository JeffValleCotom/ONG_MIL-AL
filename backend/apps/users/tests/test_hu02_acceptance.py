from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


User = get_user_model()


class HU02AuthenticationAcceptanceTests(APITestCase):
    """
    Pruebas de aceptación para HU-02 - Autenticación de usuarios.

    Validan el flujo completo de autenticación mediante
    sesiones de Django, protección CSRF y cierre de sesión.
    """

    def setUp(self):
        self.password = "MilalAcceptance123!"

        self.user = User.objects.create_user(
            username="usuario_hu02",
            email="usuario.hu02@test.com",
            first_name="Usuario",
            last_name="HU02",
            password=self.password,
        )

        self.client = APIClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse("auth-csrf")
        self.login_url = reverse("auth-login")
        self.session_url = reverse("auth-session")
        self.logout_url = reverse("auth-logout")

    def get_csrf_token(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data["csrfToken"]

    def login_user(self):
        csrf_token = self.get_csrf_token()

        return self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_ca01_user_can_login_with_valid_credentials(self):
        response = self.login_user()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["user"]["username"],
            self.user.username,
        )

    def test_ca02_invalid_credentials_are_rejected(self):
        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": "IncorrectPassword123!",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        session_response = self.client.get(
            self.session_url,
        )

        self.assertFalse(
            session_response.data["authenticated"]
        )

    def test_ca03_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_ca04_authenticated_session_is_persistent(self):
        login_response = self.login_user()

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        session_response = self.client.get(
            self.session_url,
        )

        self.assertEqual(
            session_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            session_response.data["authenticated"]
        )

        self.assertEqual(
            session_response.data["user"]["id"],
            self.user.id,
        )

    def test_ca05_login_requires_csrf_protection(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_ca06_user_can_logout_and_session_is_invalidated(self):
        login_response = self.login_user()

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        csrf_token = self.get_csrf_token()

        logout_response = self.client.post(
            self.logout_url,
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        session_response = self.client.get(
            self.session_url,
        )

        self.assertFalse(
            session_response.data["authenticated"]
        )

        self.assertIsNone(
            session_response.data["user"]
        )