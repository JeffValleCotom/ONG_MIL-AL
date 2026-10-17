from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


@override_settings(
    EMAIL_BACKEND=(
        "django.core.mail.backends.locmem.EmailBackend"
    ),
    PASSWORD_RESET_FRONTEND_URL=(
        "http://localhost:5173/password-reset"
    ),
)
class HU05AcceptanceTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="hu05_user",
            email="hu05.user@milal.org.gt",
            first_name="HU05",
            last_name="User",
            password="CurrentSecure123!",
        )

        self.change_url = reverse(
            "auth-password-change"
        )
        self.recovery_request_url = reverse(
            "auth-password-recovery-request"
        )
        self.recovery_verify_url = reverse(
            "auth-password-recovery-verify"
        )
        self.recovery_confirm_url = reverse(
            "auth-password-recovery-confirm"
        )

    def request_recovery_credentials(self):
        response = self.client.post(
            self.recovery_request_url,
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(mail.outbox),
            1,
        )

        recovery_url = next(
            line
            for line in mail.outbox[0].body.splitlines()
            if line.startswith(
                "http://localhost:5173/password-reset"
            )
        )

        query = parse_qs(
            urlparse(recovery_url).query
        )

        return (
            query["uid"][0],
            query["token"][0],
        )

    def test_authenticated_user_can_change_password_and_keep_session(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.change_url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "ChangedSecure456!",
                "new_password_confirm": "ChangedSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )
        self.assertTrue(
            self.user.check_password(
                "ChangedSecure456!"
            )
        )

        session_response = self.client.get(
            reverse("auth-session")
        )

        self.assertEqual(
            session_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            session_response.data[
                "authenticated"
            ]
        )

    def test_incorrect_current_password_does_not_change_password(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.change_url,
            {
                "current_password": "IncorrectSecure123!",
                "new_password": "ChangedSecure456!",
                "new_password_confirm": "ChangedSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )

    def test_recovery_request_and_identity_verification_succeed(self):
        uid, token = self.request_recovery_credentials()

        response = self.client.post(
            self.recovery_verify_url,
            {
                "uid": uid,
                "token": token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            response.data["valid"]
        )

    def test_complete_recovery_flow_resets_password(self):
        uid, token = self.request_recovery_credentials()

        response = self.client.post(
            self.recovery_confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password": "RecoveredSecure456!",
                "new_password_confirm": "RecoveredSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )
        self.assertTrue(
            self.user.check_password(
                "RecoveredSecure456!"
            )
        )

        reused_token_response = self.client.post(
            self.recovery_verify_url,
            {
                "uid": uid,
                "token": token,
            },
            format="json",
        )

        self.assertEqual(
            reused_token_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_nonexistent_email_receives_generic_response(self):
        existing_response = self.client.post(
            self.recovery_request_url,
            {
                "email": self.user.email,
            },
            format="json",
        )

        mail.outbox.clear()

        nonexistent_response = self.client.post(
            self.recovery_request_url,
            {
                "email": "unknown.user@milal.org.gt",
            },
            format="json",
        )

        self.assertEqual(
            nonexistent_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            nonexistent_response.data,
            existing_response.data,
        )
        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_inactive_user_does_not_receive_recovery_email(self):
        self.user.is_active = False
        self.user.save(
            update_fields=["is_active"]
        )

        response = self.client.post(
            self.recovery_request_url,
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            len(mail.outbox),
            0,
        )

    def test_weak_password_is_rejected_during_recovery(self):
        uid, token = self.request_recovery_credentials()

        response = self.client.post(
            self.recovery_confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password": "12345678",
                "new_password_confirm": "12345678",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )
