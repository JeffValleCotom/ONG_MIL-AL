from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.students.demo_data import (
    DEMO_STUDENT_PREFIX,
    DEMO_USER_PREFIX,
    get_demo_counts,
)


class DemoDataCommandsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        required_groups = (
            "ADMINISTRADOR",
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
            "RESPONSABLE_INSTITUCIONAL",
        )

        for name in required_groups:
            Group.objects.get_or_create(name=name)

    def setUp(self):
        self.temp_dir = TemporaryDirectory()

        StudentDocument = apps.get_model(
            "students",
            "StudentDocument",
        )

        self.file_field = StudentDocument._meta.get_field(
            "file"
        )

        self.original_storage = self.file_field.storage

        self.file_field.storage = FileSystemStorage(
            location=self.temp_dir.name
        )

    def tearDown(self):
        self.file_field.storage = self.original_storage
        self.temp_dir.cleanup()

    def seed(self):
        output = StringIO()

        call_command(
            "seed_demo_data",
            password="TemporaryDemoPassword123!",
            stdout=output,
        )

        return output.getvalue()

    def reset(self):
        output = StringIO()

        call_command(
            "reset_demo_data",
            confirm="RESET-DEMO-DATA",
            stdout=output,
        )

        return output.getvalue()

    def test_seed_creates_expected_demo_dataset(self):
        self.seed()

        counts = get_demo_counts()

        self.assertEqual(counts["users"], 5)
        self.assertEqual(counts["students"], 3)
        self.assertEqual(counts["assignments"], 9)
        self.assertEqual(counts["family_members"], 3)
        self.assertEqual(counts["documents"], 3)
        self.assertEqual(counts["interventions"], 6)
        self.assertEqual(counts["plans"], 6)
        self.assertEqual(counts["plan_followups"], 12)
        self.assertEqual(counts["academic_followups"], 12)
        self.assertEqual(
            counts["psychological_followups"],
            9,
        )
        self.assertEqual(counts["therapy_followups"], 9)
        self.assertEqual(counts["evaluations"], 9)
        self.assertEqual(counts["reports"], 0)
        self.assertEqual(counts["ai_insights"], 0)
        self.assertEqual(counts["alerts"], 2)
        self.assertEqual(counts["alert_events"], 3)

    def test_seed_is_idempotent(self):
        self.seed()

        first_counts = get_demo_counts()

        self.seed()

        second_counts = get_demo_counts()

        self.assertEqual(
            first_counts,
            second_counts,
        )

    def test_reset_requires_explicit_confirmation(self):
        self.seed()

        with self.assertRaises(CommandError):
            call_command(
                "reset_demo_data",
                stdout=StringIO(),
            )

        self.assertEqual(
            get_demo_counts()["students"],
            3,
        )

    def test_dry_run_does_not_delete_demo_data(self):
        self.seed()

        before = get_demo_counts()

        output = StringIO()

        call_command(
            "reset_demo_data",
            dry_run=True,
            stdout=output,
        )

        after = get_demo_counts()

        self.assertEqual(before, after)
        self.assertIn(
            "DRY RUN",
            output.getvalue(),
        )

    def test_reset_removes_only_demo_dataset(self):
        User = get_user_model()
        Student = apps.get_model(
            "students",
            "Student",
        )

        protected_admin = User.objects.create_superuser(
            username="MIL-AL",
            email="admin@example.com",
            password="ProtectedAdminPassword123!",
        )

        protected_admin.groups.add(
            Group.objects.get(name="ADMINISTRADOR")
        )

        unrelated_user = User.objects.create_user(
            username="usuario_no_demo",
            email="real@example.com",
            password="UnrelatedPassword123!",
        )

        unrelated_student = Student.objects.create(
            institutional_code="REAL-001",
            first_name="Registro",
            last_name="No Demo",
            date_of_birth="2012-01-01",
            admission_date="2025-01-01",
            is_active=True,
        )

        self.seed()
        self.reset()

        self.assertFalse(
            User.objects.filter(
                username__startswith=DEMO_USER_PREFIX
            ).exists()
        )

        self.assertFalse(
            Student.objects.filter(
                institutional_code__startswith=(
                    DEMO_STUDENT_PREFIX
                )
            ).exists()
        )

        self.assertTrue(
            User.objects.filter(
                pk=protected_admin.pk,
                username="MIL-AL",
            ).exists()
        )

        self.assertTrue(
            User.objects.filter(
                pk=unrelated_user.pk,
            ).exists()
        )

        self.assertTrue(
            Student.objects.filter(
                pk=unrelated_student.pk,
            ).exists()
        )

    def test_reset_deletes_demo_document_files(self):
        StudentDocument = apps.get_model(
            "students",
            "StudentDocument",
        )

        self.seed()

        documents = list(
            StudentDocument.objects.filter(
                student__institutional_code__startswith=(
                    DEMO_STUDENT_PREFIX
                )
            )
        )

        self.assertEqual(len(documents), 3)

        filenames = [
            document.file.name
            for document in documents
        ]

        for filename in filenames:
            self.assertTrue(
                self.file_field.storage.exists(filename)
            )

        self.reset()

        for filename in filenames:
            self.assertFalse(
                self.file_field.storage.exists(filename)
            )

        self.assertFalse(
            StudentDocument.objects.filter(
                student__institutional_code__startswith=(
                    DEMO_STUDENT_PREFIX
                )
            ).exists()
        )

    def test_structural_groups_survive_reset(self):
        self.seed()
        self.reset()

        expected = {
            "ADMINISTRADOR",
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
            "RESPONSABLE_INSTITUCIONAL",
        }

        existing = set(
            Group.objects.filter(
                name__in=expected
            ).values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(existing, expected)

    def test_demo_documents_are_written_only_to_test_storage(
        self,
    ):
        self.seed()

        StudentDocument = apps.get_model(
            "students",
            "StudentDocument",
        )

        for document in StudentDocument.objects.filter(
            student__institutional_code__startswith=(
                DEMO_STUDENT_PREFIX
            )
        ):
            path = Path(
                self.file_field.storage.path(
                    document.file.name
                )
            )

            self.assertTrue(path.exists())
            self.assertTrue(
                path.is_relative_to(
                    Path(self.temp_dir.name)
                )
            )
