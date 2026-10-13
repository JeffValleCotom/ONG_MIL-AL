from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.serializers import LoginSerializer


User = get_user_model()


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.password = "MilalTest123!"

        self.user = User.objects.create_user(
            username="docente_test",
            email="docente@test.com",
            password=self.password,
        )

    def test_valid_credentials_are_accepted(self):
        serializer = LoginSerializer(
            data={
                "username": self.user.username,
                "password": self.password,
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["user"],
            self.user,
        )

    def test_invalid_password_is_rejected(self):
        serializer = LoginSerializer(
            data={
                "username": self.user.username,
                "password": "IncorrectPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    def test_nonexistent_user_is_rejected(self):
        serializer = LoginSerializer(
            data={
                "username": "usuario_inexistente",
                "password": self.password,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    def test_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        serializer = LoginSerializer(
            data={
                "username": self.user.username,
                "password": self.password,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )