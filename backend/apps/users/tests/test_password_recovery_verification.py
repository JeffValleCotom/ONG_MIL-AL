from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordRecoveryVerificationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="recovery_verify_user",
            email="verify.user@milal.org.gt",
            password="CurrentSecure123!",
        )

        self.verify_url = reverse(
            "auth-password-recovery-verify"
        )
        self.confirm_url = reverse(
            "auth-password-recovery-confirm"
        )

        self.uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )
        self.token = default_token_generator.make_token(
            self.user
        )

    def test_valid_uid_and_token_are_accepted(self):
        response = self.client.post(
            self.verify_url,
            {
                "uid": self.uid,
                "token": self.token,
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

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            self.verify_url,
            {
                "uid": self.uid,
                "token": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_uid_is_rejected(self):
        response = self.client.post(
            self.verify_url,
            {
                "uid": "invalid-uid",
                "token": self.token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save(
            update_fields=["is_active"]
        )

        response = self.client.post(
            self.verify_url,
            {
                "uid": self.uid,
                "token": self.token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_valid_token_can_reset_password(self):
        response = self.client.post(
            self.confirm_url,
            {
                "uid": self.uid,
                "token": self.token,
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

        self.assertTrue(
            self.user.check_password(
                "RecoveredSecure456!"
            )
        )
        self.assertFalse(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )

    def test_token_cannot_be_reused_after_password_reset(self):
        first_response = self.client.post(
            self.confirm_url,
            {
                "uid": self.uid,
                "token": self.token,
                "new_password": "RecoveredSecure456!",
                "new_password_confirm": "RecoveredSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            self.confirm_url,
            {
                "uid": self.uid,
                "token": self.token,
                "new_password": "AnotherSecure789!",
                "new_password_confirm": "AnotherSecure789!",
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "RecoveredSecure456!"
            )
        )

    def test_mismatched_passwords_do_not_reset_password(self):
        response = self.client.post(
            self.confirm_url,
            {
                "uid": self.uid,
                "token": self.token,
                "new_password": "RecoveredSecure456!",
                "new_password_confirm": "DifferentSecure789!",
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

    def test_weak_password_does_not_reset_password(self):
        response = self.client.post(
            self.confirm_url,
            {
                "uid": self.uid,
                "token": self.token,
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