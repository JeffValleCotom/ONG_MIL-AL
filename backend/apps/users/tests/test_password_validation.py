from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordValidationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="validation_user",
            email="validation.user@milal.org.gt",
            first_name="Validation",
            last_name="User",
            password="CurrentSecure123!",
        )

        self.client.force_login(
            self.user
        )

        self.url = reverse(
            "auth-password-change"
        )

    def change_password(self, new_password):
        return self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": new_password,
                "new_password_confirm": new_password,
            },
            format="json",
        )

    def assert_password_was_not_changed(self):
        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )

    def test_password_below_minimum_length_is_rejected(self):
        response = self.change_password(
            "Ab1!"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "new_password",
            response.data,
        )

        self.assert_password_was_not_changed()

    def test_common_password_is_rejected(self):
        response = self.change_password(
            "password123"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "new_password",
            response.data,
        )

        self.assert_password_was_not_changed()

    def test_numeric_password_is_rejected(self):
        response = self.change_password(
            "1234567890123456"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "new_password",
            response.data,
        )

        self.assert_password_was_not_changed()

    def test_password_similar_to_username_is_rejected(self):
        response = self.change_password(
            "validation_user"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "new_password",
            response.data,
        )

        self.assert_password_was_not_changed()

    def test_valid_password_is_accepted(self):
        response = self.change_password(
            "CompletelyNewSecure456!"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "CompletelyNewSecure456!"
            )
        )
