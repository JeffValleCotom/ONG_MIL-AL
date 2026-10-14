from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


User = get_user_model()


class LogoutTests(APITestCase):
    def setUp(self):
        self.password = "MilalLogout123!"

        self.user = User.objects.create_user(
            username="docente_logout",
            email="docente.logout@test.com",
            password=self.password,
        )

        self.client = APIClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse("auth-csrf")
        self.login_url = reverse("auth-login")
        self.logout_url = reverse("auth-logout")
        self.session_url = reverse("auth-session")

    def get_csrf_token(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data["csrfToken"]

    def login_user(self):
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
            status.HTTP_200_OK,
        )

    def test_authenticated_user_can_logout(self):
        self.login_user()

        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["detail"],
            "Sesión cerrada correctamente.",
        )

    def test_logout_without_csrf_is_rejected(self):
        self.login_user()

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_logout_invalidates_session(self):
        self.login_user()

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

        self.assertEqual(
            session_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            session_response.data["authenticated"]
        )

        self.assertIsNone(
            session_response.data["user"]
        )