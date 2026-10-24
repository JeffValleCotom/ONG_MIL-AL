from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from apps.users.permission_catalog import (
    PLATFORM_PERMISSION_CODENAMES,
)
from apps.users.role_permissions import ROLE_PERMISSIONS
from apps.users.roles import INSTITUTIONAL_ROLES


User = get_user_model()


class RolePermissionTests(TestCase):

    def test_role_permission_matrix_uses_defined_roles_and_permissions(self):
        self.assertEqual(
            set(ROLE_PERMISSIONS.keys()),
            set(INSTITUTIONAL_ROLES),
        )

        assigned_permissions = {
            codename
            for permission_codenames in ROLE_PERMISSIONS.values()
            for codename in permission_codenames
        }

        self.assertEqual(
            assigned_permissions,
            set(PLATFORM_PERMISSION_CODENAMES),
        )

    def test_database_role_permissions_match_defined_matrix(self):
        for role_name, expected_codenames in ROLE_PERMISSIONS.items():
            group = Group.objects.get(
                name=role_name,
            )

            stored_codenames = set(
                group.permissions.filter(
                    content_type__app_label="users",
                    content_type__model="user",
                    codename__in=PLATFORM_PERMISSION_CODENAMES,
                ).values_list(
                    "codename",
                    flat=True,
                )
            )

            self.assertEqual(
                stored_codenames,
                set(expected_codenames),
            )

    def test_user_with_multiple_roles_receives_permission_union(self):
        user = User.objects.create_user(
            username="multi_role_user",
            password="MilalMultiRole123!",
        )

        docente = Group.objects.get(
            name="DOCENTE",
        )
        psicologo = Group.objects.get(
            name="PSICOLOGO",
        )

        user.groups.add(
            docente,
            psicologo,
        )

        expected_permissions = {
            f"users.{codename}"
            for codename in (
                set(ROLE_PERMISSIONS["DOCENTE"])
                | set(ROLE_PERMISSIONS["PSICOLOGO"])
            )
        }

        effective_permissions = user.get_group_permissions()

        self.assertTrue(
            expected_permissions.issubset(
                effective_permissions
            )
        )

    def test_student_assignment_permission_is_restricted_to_responsible_role(
        self,
    ):
        permission_codename = "manage_student_assignments"
        expected_role = "RESPONSABLE_INSTITUCIONAL"

        configured_roles = {
            role_name
            for role_name, permission_codenames
            in ROLE_PERMISSIONS.items()
            if permission_codename in permission_codenames
        }

        self.assertEqual(
            configured_roles,
            {expected_role},
        )

        database_roles = set(
            Group.objects.filter(
                permissions__content_type__app_label="users",
                permissions__content_type__model="user",
                permissions__codename=permission_codename,
            ).values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            database_roles,
            {expected_role},
        )