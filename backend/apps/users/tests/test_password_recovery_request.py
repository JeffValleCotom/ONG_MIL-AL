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
class PasswordRecoveryRequestTests(APITestCase):

    def setUp(self):
        self.url = reverse(
            "auth-password-recovery-request"
        )

        self.user = User.objects.create_user(
            username="recovery_user",
            email="recovery.user@milal.org.gt",
            password="CurrentSecure123!",
        )

    def test_existing_active_user_receives_recovery_email(self):
        response = self.client.post(
            self.url,
            {
                "email": "recovery.user@milal.org.gt",
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

        message = mail.outbox[0]

        self.assertEqual(
            message.to,
            [
                "recovery.user@milal.org.gt",
            ],
        )

        self.assertIn(
            "http://localhost:5173/password-reset",
            message.body,
        )
        self.assertIn(
            "uid=",
            message.body,
        )
        self.assertIn(
            "token=",
            message.body,
        )

    def test_response_does_not_expose_uid_or_token(self):
        response = self.client.post(
            self.url,
            {
                "email": "recovery.user@milal.org.gt",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "uid",
            response.data,
        )
        self.assertNotIn(
            "token",
            response.data,
        )

    def test_nonexistent_email_returns_same_generic_response(self):
        existing_response = self.client.post(
            self.url,
            {
                "email": "recovery.user@milal.org.gt",
            },
            format="json",
        )

        mail.outbox.clear()

        nonexistent_response = self.client.post(
            self.url,
            {
                "email": "does.not.exist@milal.org.gt",
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
            self.url,
            {
                "email": "recovery.user@milal.org.gt",
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

    def test_user_without_usable_password_does_not_receive_email(self):
        self.user.set_unusable_password()
        self.user.save(
            update_fields=["password"]
        )

        response = self.client.post(
            self.url,
            {
                "email": "recovery.user@milal.org.gt",
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

    def test_email_lookup_is_case_insensitive(self):
        response = self.client.post(
            self.url,
            {
                "email": "RECOVERY.USER@MILAL.ORG.GT",
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

    def test_invalid_email_format_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "email": "correo-invalido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )
