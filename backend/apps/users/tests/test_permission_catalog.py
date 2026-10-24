from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from apps.users.permission_catalog import (
    PLATFORM_PERMISSION_CODENAMES,
    PLATFORM_PERMISSIONS,
)


class PermissionCatalogTests(TestCase):

    def test_permission_catalog_contains_17_unique_permissions(self):
        self.assertEqual(
            len(PLATFORM_PERMISSIONS),
            17,
        )

        self.assertEqual(
            len(PLATFORM_PERMISSION_CODENAMES),
            17,
        )

        self.assertEqual(
            len(set(PLATFORM_PERMISSION_CODENAMES)),
            17,
        )

        self.assertIn(
            "manage_student_assignments",
            PLATFORM_PERMISSION_CODENAMES,
        )

    def test_permission_catalog_is_persisted_in_database(self):
        user_content_type = ContentType.objects.get(
            app_label="users",
            model="user",
        )

        stored_permissions = Permission.objects.filter(
            content_type=user_content_type,
            codename__in=PLATFORM_PERMISSION_CODENAMES,
        ).values_list(
            "codename",
            "name",
        )

        self.assertEqual(
            dict(stored_permissions),
            dict(PLATFORM_PERMISSIONS),
        )
