from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class PasswordChangeTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="password_user",
            email="password.user@milal.org.gt",
            password="CurrentSecure123!",
        )

        self.url = reverse(
            "auth-password-change"
        )

    def test_authenticated_user_can_change_own_password(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "NewSecure456!",
                "new_password_confirm": "NewSecure456!",
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
                "NewSecure456!"
            )
        )

    def test_old_password_stops_working_after_change(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "NewSecure456!",
                "new_password_confirm": "NewSecure456!",
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

    def test_session_remains_authenticated_after_change(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "NewSecure456!",
                "new_password_confirm": "NewSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
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
            self.url,
            {
                "current_password": "IncorrectPassword123!",
                "new_password": "NewSecure456!",
                "new_password_confirm": "NewSecure456!",
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

    def test_mismatched_new_passwords_do_not_change_password(self):
        self.client.force_login(
            self.user
        )

        response = self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "NewSecure456!",
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

    def test_anonymous_user_cannot_change_password(self):
        response = self.client.post(
            self.url,
            {
                "current_password": "CurrentSecure123!",
                "new_password": "NewSecure456!",
                "new_password_confirm": "NewSecure456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "CurrentSecure123!"
            )
        )

    def test_administrator_cannot_change_another_user_password(self):
        administrator = User.objects.create_user(
            username="password_admin",
            password="AdminSecure123!",
        )
        administrator.groups.add(
            Group.objects.get(
                name="ADMINISTRADOR",
            )
        )

        target_user = User.objects.create_user(
            username="password_target",
            password="TargetSecure123!",
        )

        self.client.force_login(
            administrator
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                kwargs={
                    "pk": target_user.pk,
                },
            ),
            {
                "password": "ChangedByAdmin456!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        target_user.refresh_from_db()

        self.assertTrue(
            target_user.check_password(
                "TargetSecure123!"
            )
        )
