from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


User = get_user_model()


class SessionAuthenticationTests(APITestCase):
    def setUp(self):
        self.password = "MilalSession123!"

        self.user = User.objects.create_user(
            username="docente_session",
            email="docente.session@test.com",
            password=self.password,
        )

        self.client = APIClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse("auth-csrf")
        self.login_url = reverse("auth-login")
        self.session_url = reverse("auth-session")

    def get_csrf_token(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "csrfToken",
            response.data,
        )

        return response.data["csrfToken"]

    def test_csrf_endpoint_returns_token(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["csrfToken"]
        )

        self.assertIn(
            settings.CSRF_COOKIE_NAME,
            self.client.cookies,
        )

    def test_session_endpoint_reports_unauthenticated_user(self):
        response = self.client.get(
            self.session_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["authenticated"]
        )

        self.assertIsNone(
            response.data["user"]
        )

    def test_login_without_csrf_is_rejected(self):
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

    def test_valid_login_creates_session(self):
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

        self.assertEqual(
            response.data["user"]["username"],
            self.user.username,
        )

        self.assertIn(
            settings.SESSION_COOKIE_NAME,
            self.client.cookies,
        )

    def test_session_endpoint_restores_authenticated_user(self):
        csrf_token = self.get_csrf_token()

        login_response = self.client.post(
            self.login_url,
            {
                "username": self.user.username,
                "password": self.password,
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.get(
            self.session_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["authenticated"]
        )

        self.assertEqual(
            response.data["user"]["id"],
            self.user.id,
        )

        self.assertEqual(
            response.data["user"]["username"],
            self.user.username,
        )

    def test_invalid_credentials_do_not_create_session(self):
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

        self.assertNotIn(
            settings.SESSION_COOKIE_NAME,
            self.client.cookies,
        )