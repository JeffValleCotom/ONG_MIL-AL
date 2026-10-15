from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class FunctionalAuthorizationTests(APITestCase):

    def setUp(self):
        self.target_user = User.objects.create_user(
            username="target_user",
            password="MilalTarget123!",
        )

    def test_manage_users_permission_authorizes_user_management(self):
        operator = User.objects.create_user(
            username="user_manager",
            password="MilalManager123!",
        )

        docente = Group.objects.get(
            name="DOCENTE",
        )

        manage_users = Permission.objects.get(
            content_type__app_label="users",
            content_type__model="user",
            codename="manage_users",
        )

        docente.permissions.add(
            manage_users
        )
        operator.groups.add(
            docente
        )

        self.client.force_login(operator)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_administrator_role_without_permission_is_not_authorized(self):
        operator = User.objects.create_user(
            username="admin_without_permission",
            password="MilalAdmin123!",
        )

        administrator = Group.objects.get(
            name="ADMINISTRADOR",
        )

        manage_users = Permission.objects.get(
            content_type__app_label="users",
            content_type__model="user",
            codename="manage_users",
        )

        administrator.permissions.remove(
            manage_users
        )
        operator.groups.add(
            administrator
        )

        self.client.force_login(operator)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_roles_functionality_requires_manage_roles_permission(self):
        operator = User.objects.create_user(
            username="roles_operator",
            password="MilalRoles123!",
        )

        administrator = Group.objects.get(
            name="ADMINISTRADOR",
        )

        manage_roles = Permission.objects.get(
            content_type__app_label="users",
            content_type__model="user",
            codename="manage_roles",
        )

        administrator.permissions.remove(
            manage_roles
        )
        operator.groups.add(
            administrator
        )

        self.client.force_login(operator)

        response = self.client.get(
            reverse(
                "user-roles",
                kwargs={
                    "pk": self.target_user.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_django_superuser_does_not_bypass_platform_permissions(self):
        superuser = User.objects.create_superuser(
            username="technical_superuser",
            email="superuser@test.com",
            password="MilalSuper123!",
        )

        self.client.force_login(superuser)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )