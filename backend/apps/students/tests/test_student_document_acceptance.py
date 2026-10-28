import io
import zipfile
import hashlib
from pathlib import Path
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.test import APITestCase

from apps.students.models import (
    Student,
    StudentDocument,
    StudentProfessionalAssignment,
)
from apps.students.document_validation import (
    DocumentValidationError,
    validate_uploaded_document,
)

User = get_user_model()


class StudentDocumentAcceptanceTests(APITestCase):
    def setUp(self):
        self.responsible = User.objects.create_user(
            username="document_acceptance_responsible",
            password="MilalDocumentAcceptance123!",
        )
        self.responsible.groups.add(
            Group.objects.get(
                name="RESPONSABLE_INSTITUCIONAL"
            )
        )

        self.student = Student.objects.create(
            institutional_code="DOC-A-001",
            first_name="Ana",
            last_name="Lopez",
            date_of_birth="2015-05-10",
            admission_date="2023-01-15",
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        self._temporary_storage_directory = (
            tempfile.TemporaryDirectory()
        )

        document_file_field = (
            StudentDocument._meta.get_field("file")
        )

        self._original_document_storage = (
            document_file_field.storage
        )

        document_file_field.storage = FileSystemStorage(
            location=(
                self._temporary_storage_directory.name
            )
        )

        self.addCleanup(
            setattr,
            document_file_field,
            "storage",
            self._original_document_storage,
        )
        self.addCleanup(
            self._temporary_storage_directory.cleanup
        )

    def documents_url(self):
        return reverse(
            "student-documents",
            kwargs={
                "pk": self.student.pk,
            },
        )

    def create_valid_docx_content(self):
        buffer = io.BytesIO()

        with zipfile.ZipFile(
            buffer,
            mode="w",
        ) as archive:
            archive.writestr(
                "[Content_Types].xml",
                (
                    '<?xml version="1.0"?>'
                    "<Types></Types>"
                ),
            )
            archive.writestr(
                "word/document.xml",
                (
                    '<?xml version="1.0"?>'
                    "<document></document>"
                ),
            )

        return buffer.getvalue()

    def create_valid_pdf_upload(
        self,
        filename="document.pdf",
    ):
        return SimpleUploadedFile(
            filename,
            (
                b"%PDF-1.4\n"
                b"TASK60\n"
                b"%%EOF\n"
            ),
            content_type="application/pdf",
        )

    def upload_document(
        self,
        user,
        context,
        document_type,
        filename,
    ):
        self.client.force_authenticate(
            user=user
        )

        return self.client.post(
            (
                f"{self.documents_url()}"
                f"?context={context}"
            ),
            {
                "document_type": document_type,
                "file": self.create_valid_pdf_upload(
                    filename
                ),
            },
            format="multipart",
        )

    def test_other_allowed_document_formats_are_accepted(
        self,
    ):
        cases = [
            {
                "filename": "foto.JPG",
                "content": (
                    b"\xff\xd8\xff"
                    b"TASK60-JPEG"
                    b"\xff\xd9"
                ),
                "declared_mime": "image/jpeg",
                "expected_mime": "image/jpeg",
                "expected_extension": ".jpg",
            },
            {
                "filename": "imagen.PNG",
                "content": (
                    b"\x89PNG\r\n\x1a\n"
                    b"\x00\x00\x00\r"
                    b"IHDR"
                    b"TASK60-PNG"
                ),
                "declared_mime": "image/png",
                "expected_mime": "image/png",
                "expected_extension": ".png",
            },
            {
                "filename": "informe.DOCX",
                "content": self.create_valid_docx_content(),
                "declared_mime": "application/zip",
                "expected_mime": (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                "expected_extension": ".docx",
            },
        ]

        for case in cases:
            with self.subTest(
                filename=case["filename"]
            ):
                uploaded_file = SimpleUploadedFile(
                    case["filename"],
                    case["content"],
                    content_type=case["declared_mime"],
                )

                response = self.client.post(
                    (
                        f"{self.documents_url()}"
                        "?context=RESPONSABLE_INSTITUCIONAL"
                    ),
                    {
                        "document_type": "IDENTIFICACION",
                        "file": uploaded_file,
                    },
                    format="multipart",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                )

                document = StudentDocument.objects.get(
                    pk=response.data["id"]
                )

                self.assertEqual(
                    document.original_filename,
                    case["filename"],
                )
                self.assertEqual(
                    document.mime_type,
                    case["expected_mime"],
                )
                self.assertEqual(
                    document.size_bytes,
                    len(case["content"]),
                )
                self.assertEqual(
                    document.sha256,
                    hashlib.sha256(
                        case["content"]
                    ).hexdigest(),
                )
                self.assertEqual(
                    Path(document.file.name).suffix,
                    case["expected_extension"],
                )
                self.assertTrue(
                    document.file.storage.exists(
                        document.file.name
                    )
                )

    def test_invalid_document_files_are_rejected_without_persistence(
        self,
    ):
        cases = [
            {
                "filename": "archivo.exe",
                "content": b"MZ-TASK60",
                "declared_mime": "application/octet-stream",
            },
            {
                "filename": "archivo.pdf.exe",
                "content": (
                    b"%PDF-1.4\n"
                    b"TASK60\n"
                    b"%%EOF\n"
                ),
                "declared_mime": "application/octet-stream",
            },
            {
                "filename": "archivo.pdf",
                "content": b"NOT-A-REAL-PDF",
                "declared_mime": "application/pdf",
            },
            {
                "filename": "archivo.pdf",
                "content": (
                    b"%PDF-1.4\n"
                    b"TASK60\n"
                    b"%%EOF\n"
                ),
                "declared_mime": "image/png",
            },
            {
                "filename": "archivo.docx",
                "content": b"NOT-A-DOCX-ZIP",
                "declared_mime": (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            },
        ]

        for case in cases:
            with self.subTest(
                filename=case["filename"],
                declared_mime=case["declared_mime"],
            ):
                uploaded_file = SimpleUploadedFile(
                    case["filename"],
                    case["content"],
                    content_type=case["declared_mime"],
                )

                response = self.client.post(
                    (
                        f"{self.documents_url()}"
                        "?context=RESPONSABLE_INSTITUCIONAL"
                    ),
                    {
                        "document_type": "IDENTIFICACION",
                        "file": uploaded_file,
                    },
                    format="multipart",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(
                    "file",
                    response.data,
                )
                self.assertEqual(
                    StudentDocument.objects.count(),
                    0,
                )

                stored_files = [
                    path
                    for path in Path(
                        self._temporary_storage_directory.name
                    ).rglob("*")
                    if path.is_file()
                ]

                self.assertEqual(
                    stored_files,
                    [],
                )

    def test_document_file_limits_are_enforced_without_persistence(
        self,
    ):
        oversized_content = (
            b"%PDF-"
            + b"A" * (10 * 1024 * 1024)
        )

        cases = [
            {
                "filename": "empty.pdf",
                "content": b"",
                "declared_mime": "application/pdf",
            },
            {
                "filename": "document",
                "content": (
                    b"%PDF-1.4\n"
                    b"TASK60\n"
                    b"%%EOF\n"
                ),
                "declared_mime": "application/pdf",
            },
            {
                "filename": "oversized.pdf",
                "content": oversized_content,
                "declared_mime": "application/pdf",
            },
        ]

        for case in cases:
            with self.subTest(
                filename=case["filename"]
            ):
                uploaded_file = SimpleUploadedFile(
                    case["filename"],
                    case["content"],
                    content_type=case["declared_mime"],
                )

                response = self.client.post(
                    (
                        f"{self.documents_url()}"
                        "?context=RESPONSABLE_INSTITUCIONAL"
                    ),
                    {
                        "document_type": "IDENTIFICACION",
                        "file": uploaded_file,
                    },
                    format="multipart",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(
                    "file",
                    response.data,
                )
                self.assertEqual(
                    StudentDocument.objects.count(),
                    0,
                )

                stored_files = [
                    path
                    for path in Path(
                        self._temporary_storage_directory.name
                    ).rglob("*")
                    if path.is_file()
                ]

                self.assertEqual(
                    stored_files,
                    [],
                )

    def test_validator_rejects_original_filename_over_255_characters(
        self,
    ):
        class UploadedFileWithLongName(io.BytesIO):
            def __init__(
                self,
                name,
                content,
                content_type,
            ):
                super().__init__(content)
                self.name = name
                self.size = len(content)
                self.content_type = content_type

        long_filename = (
            "a" * 252
            + ".pdf"
        )

        self.assertEqual(
            len(long_filename),
            256,
        )

        uploaded_file = UploadedFileWithLongName(
            name=long_filename,
            content=(
                b"%PDF-1.4\n"
                b"TASK60\n"
                b"%%EOF\n"
            ),
            content_type="application/pdf",
        )

        with self.assertRaisesRegex(
            DocumentValidationError,
            "255 caracteres",
        ):
            validate_uploaded_document(
                uploaded_file
            )

    def test_responsible_can_upload_valid_pdf_document(
        self,
    ):
        file_content = (
            b"%PDF-1.4\n"
            b"1 0 obj\n"
            b"<< /Type /Catalog >>\n"
            b"endobj\n"
            b"%%EOF\n"
        )

        uploaded_file = SimpleUploadedFile(
            "Identificacion.PDF",
            file_content,
            content_type="application/pdf",
        )

        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "document_type": "IDENTIFICACION",
                "description": (
                    "Documento de prueba TASK-60"
                ),
                "file": uploaded_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            StudentDocument.objects.count(),
            1,
        )

        document = StudentDocument.objects.get()

        expected_sha256 = hashlib.sha256(
            file_content
        ).hexdigest()

        self.assertEqual(
            document.student,
            self.student,
        )
        self.assertEqual(
            document.document_type,
            StudentDocument.DocumentType.IDENTIFICACION,
        )
        self.assertEqual(
            document.original_filename,
            "Identificacion.PDF",
        )
        self.assertEqual(
            document.mime_type,
            "application/pdf",
        )
        self.assertEqual(
            document.size_bytes,
            len(file_content),
        )
        self.assertEqual(
            document.sha256,
            expected_sha256,
        )
        self.assertEqual(
            document.created_by,
            self.responsible,
        )
        self.assertEqual(
            document.updated_by,
            self.responsible,
        )

        stored_name = document.file.name.replace(
            "\\",
            "/",
        )

        self.assertTrue(
            stored_name.startswith(
                (
                    f"students/{self.student.pk}/"
                    "documents/"
                )
            )
        )
        self.assertEqual(
            Path(stored_name).suffix,
            ".pdf",
        )
        self.assertNotEqual(
            Path(stored_name).name,
            document.original_filename,
        )
        self.assertTrue(
            document.file.storage.exists(
                document.file.name
            )
        )

        self.assertEqual(
            response.data["original_filename"],
            "Identificacion.PDF",
        )
        self.assertEqual(
            response.data["mime_type"],
            "application/pdf",
        )
        self.assertEqual(
            response.data["size_bytes"],
            len(file_content),
        )
        self.assertEqual(
            response.data["sha256"],
            expected_sha256,
        )

    def test_assigned_docente_can_upload_academic_document(
        self,
    ):
        docente = User.objects.create_user(
            username="document_acceptance_docente",
            password="MilalDocumentAcceptance123!",
        )
        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            ),
            {
                "document_type": "ACADEMICO",
                "file": self.create_valid_pdf_upload(
                    "academic.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = StudentDocument.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            document.document_type,
            StudentDocument.DocumentType.ACADEMICO,
        )
        self.assertEqual(
            document.created_by,
            docente,
        )

    def test_docente_document_access_respects_context_and_assignment(
        self,
    ):
        docente = User.objects.create_user(
            username="document_scope_docente",
            password="MilalDocumentAcceptance123!",
        )
        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        unassigned_student = Student.objects.create(
            institutional_code="DOC-A-002",
            first_name="Carlos",
            last_name="Perez",
            date_of_birth="2014-08-20",
            admission_date="2023-02-10",
        )

        self.client.force_authenticate(
            user=docente
        )

        wrong_type_response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            ),
            {
                "document_type": "IDENTIFICACION",
                "file": self.create_valid_pdf_upload(),
            },
            format="multipart",
        )

        self.assertEqual(
            wrong_type_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        unassigned_url = reverse(
            "student-documents",
            kwargs={
                "pk": unassigned_student.pk,
            },
        )

        unassigned_response = self.client.post(
            f"{unassigned_url}?context=DOCENTE",
            {
                "document_type": "ACADEMICO",
                "file": self.create_valid_pdf_upload(
                    "unassigned.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            unassigned_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(
            StudentDocument.objects.count(),
            0,
        )

    def test_document_query_is_filtered_by_context(
        self,
    ):
        identification_response = self.upload_document(
            user=self.responsible,
            context="RESPONSABLE_INSTITUCIONAL",
            document_type="IDENTIFICACION",
            filename="identification.pdf",
        )

        self.assertEqual(
            identification_response.status_code,
            status.HTTP_201_CREATED,
        )

        docente = User.objects.create_user(
            username="document_query_docente",
            password="MilalDocumentAcceptance123!",
        )
        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        academic_response = self.upload_document(
            user=docente,
            context="DOCENTE",
            document_type="ACADEMICO",
            filename="academic-query.pdf",
        )

        self.assertEqual(
            academic_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=docente
        )

        docente_response = self.client.get(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            )
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_200_OK,
        )

        docente_ids = {
            item["id"]
            for item in docente_response.data["items"]
        }

        self.assertEqual(
            docente_ids,
            {
                academic_response.data["id"],
            },
        )

        self.client.force_authenticate(
            user=self.responsible
        )

        responsible_response = self.client.get(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            )
        )

        self.assertEqual(
            responsible_response.status_code,
            status.HTTP_200_OK,
        )

        responsible_ids = {
            item["id"]
            for item in responsible_response.data["items"]
        }

        self.assertEqual(
            responsible_ids,
            {
                identification_response.data["id"],
            },
        )

    def test_document_download_enforces_context_isolation(
        self,
    ):
        identification_response = self.upload_document(
            user=self.responsible,
            context="RESPONSABLE_INSTITUCIONAL",
            document_type="IDENTIFICACION",
            filename="private-identification.pdf",
        )

        self.assertEqual(
            identification_response.status_code,
            status.HTTP_201_CREATED,
        )

        docente = User.objects.create_user(
            username="document_download_docente",
            password="MilalDocumentAcceptance123!",
        )
        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        academic_response = self.upload_document(
            user=docente,
            context="DOCENTE",
            document_type="ACADEMICO",
            filename="academic-download.pdf",
        )

        self.assertEqual(
            academic_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=docente
        )

        academic_download_url = reverse(
            "student-document-download",
            kwargs={
                "pk": self.student.pk,
                "document_id": (
                    academic_response.data["id"]
                ),
            },
        )

        download_response = self.client.get(
            (
                f"{academic_download_url}"
                "?context=DOCENTE"
            )
        )

        self.assertEqual(
            download_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            download_response["Content-Type"],
            "application/pdf",
        )
        self.assertEqual(
            download_response["Cache-Control"],
            "private, no-store",
        )
        self.assertEqual(
            download_response[
                "X-Content-Type-Options"
            ],
            "nosniff",
        )
        self.assertIn(
            "academic-download.pdf",
            download_response[
                "Content-Disposition"
            ],
        )

        downloaded_content = b"".join(
            download_response.streaming_content
        )

        self.assertEqual(
            downloaded_content,
            (
                b"%PDF-1.4\n"
                b"TASK60\n"
                b"%%EOF\n"
            ),
        )

        forbidden_download_url = reverse(
            "student-document-download",
            kwargs={
                "pk": self.student.pk,
                "document_id": (
                    identification_response.data["id"]
                ),
            },
        )

        forbidden_response = self.client.get(
            (
                f"{forbidden_download_url}"
                "?context=DOCENTE"
            )
        )

        self.assertEqual(
            forbidden_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_assigned_specialists_can_upload_documents_for_their_context(
        self,
    ):
        cases = [
            {
                "role": "PSICOLOGO",
                "document_type": "PSICOLOGICO",
                "username": "document_acceptance_psychologist",
                "filename": "psychological.pdf",
            },
            {
                "role": "TERAPEUTA",
                "document_type": "TERAPEUTICO",
                "username": "document_acceptance_therapist",
                "filename": "therapeutic.pdf",
            },
        ]

        for case in cases:
            with self.subTest(
                role=case["role"]
            ):
                professional = User.objects.create_user(
                    username=case["username"],
                    password=(
                        "MilalDocumentAcceptance123!"
                    ),
                )
                professional.groups.add(
                    Group.objects.get(
                        name=case["role"]
                    )
                )

                StudentProfessionalAssignment.objects.create(
                    student=self.student,
                    professional=professional,
                    professional_role=case["role"],
                    assigned_by=self.responsible,
                )

                response = self.upload_document(
                    user=professional,
                    context=case["role"],
                    document_type=case["document_type"],
                    filename=case["filename"],
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_201_CREATED,
                )

                document = StudentDocument.objects.get(
                    pk=response.data["id"]
                )

                self.assertEqual(
                    document.document_type,
                    case["document_type"],
                )
                self.assertEqual(
                    document.created_by,
                    professional,
                )
                self.assertEqual(
                    document.updated_by,
                    professional,
                )

    def test_user_cannot_use_document_context_for_role_not_owned(
        self,
    ):
        docente = User.objects.create_user(
            username="document_invalid_context_docente",
            password="MilalDocumentAcceptance123!",
        )
        docente.groups.add(
            Group.objects.get(
                name="DOCENTE"
            )
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=PSICOLOGO"
            ),
            {
                "document_type": "PSICOLOGICO",
                "file": self.create_valid_pdf_upload(
                    "unauthorized-context.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            StudentDocument.objects.count(),
            0,
        )

    def test_inactive_or_wrong_role_assignment_cannot_access_documents(
        self,
    ):
        professional = User.objects.create_user(
            username="document_assignment_scope",
            password="MilalDocumentAcceptance123!",
        )
        professional.groups.add(
            Group.objects.get(
                name="DOCENTE"
            ),
            Group.objects.get(
                name="PSICOLOGO"
            ),
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
            is_active=False,
            unassigned_at=timezone.now(),
        )

        self.client.force_authenticate(
            user=professional
        )

        inactive_response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            ),
            {
                "document_type": "ACADEMICO",
                "file": self.create_valid_pdf_upload(
                    "inactive-assignment.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            inactive_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        wrong_role_response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=PSICOLOGO"
            ),
            {
                "document_type": "PSICOLOGICO",
                "file": self.create_valid_pdf_upload(
                    "wrong-role-assignment.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            wrong_role_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertEqual(
            StudentDocument.objects.count(),
            0,
        )

    def test_multi_role_document_contexts_remain_isolated(
        self,
    ):
        professional = User.objects.create_user(
            username="document_multi_role",
            password="MilalDocumentAcceptance123!",
        )
        professional.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=professional,
            professional_role="PSICOLOGO",
            assigned_by=self.responsible,
        )

        academic_response = self.upload_document(
            user=professional,
            context="DOCENTE",
            document_type="ACADEMICO",
            filename="multi-academic.pdf",
        )

        self.assertEqual(
            academic_response.status_code,
            status.HTTP_201_CREATED,
        )

        psychological_response = self.upload_document(
            user=professional,
            context="PSICOLOGO",
            document_type="PSICOLOGICO",
            filename="multi-psychological.pdf",
        )

        self.assertEqual(
            psychological_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=professional
        )

        docente_response = self.client.get(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            )
        )

        self.assertEqual(
            docente_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {
                item["id"]
                for item in docente_response.data["items"]
            },
            {
                academic_response.data["id"],
            },
        )

        psychologist_response = self.client.get(
            (
                f"{self.documents_url()}"
                "?context=PSICOLOGO"
            )
        )

        self.assertEqual(
            psychologist_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            {
                item["id"]
                for item in psychologist_response.data["items"]
            },
            {
                psychological_response.data["id"],
            },
        )

        academic_download_url = reverse(
            "student-document-download",
            kwargs={
                "pk": self.student.pk,
                "document_id": (
                    academic_response.data["id"]
                ),
            },
        )

        cross_context_response = self.client.get(
            (
                f"{academic_download_url}"
                "?context=PSICOLOGO"
            )
        )

        self.assertEqual(
            cross_context_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_other_document_type_requires_detail(
        self,
    ):
        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "document_type": "OTRO",
                "file": self.create_valid_pdf_upload(
                    "other-without-detail.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "document_type_detail",
            response.data,
        )
        self.assertEqual(
            StudentDocument.objects.count(),
            0,
        )

    def test_document_type_detail_is_only_allowed_for_other(
        self,
    ):
        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "document_type": "IDENTIFICACION",
                "document_type_detail": (
                    "Detalle que no debería aceptarse"
                ),
                "file": self.create_valid_pdf_upload(
                    "identification-detail.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            "document_type_detail",
            response.data,
        )
        self.assertEqual(
            StudentDocument.objects.count(),
            0,
        )

    def test_other_document_type_accepts_specific_detail(
        self,
    ):
        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "document_type": "OTRO",
                "document_type_detail": (
                    "Constancia de actividad externa"
                ),
                "file": self.create_valid_pdf_upload(
                    "other-valid.pdf"
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = StudentDocument.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            document.document_type,
            StudentDocument.DocumentType.OTRO,
        )
        self.assertEqual(
            document.document_type_detail,
            "Constancia de actividad externa",
        )

    def test_generic_declared_mime_uses_backend_canonical_mime(
        self,
    ):
        uploaded_file = SimpleUploadedFile(
            "generic.pdf",
            (
                b"%PDF-1.4\n"
                b"TASK60-GENERIC-MIME\n"
                b"%%EOF\n"
            ),
            content_type="application/octet-stream",
        )

        response = self.client.post(
            (
                f"{self.documents_url()}"
                "?context=RESPONSABLE_INSTITUCIONAL"
            ),
            {
                "document_type": "IDENTIFICACION",
                "file": uploaded_file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = StudentDocument.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            document.mime_type,
            "application/pdf",
        )
        self.assertEqual(
            response.data["mime_type"],
            "application/pdf",
        )

    def test_role_without_functional_permission_cannot_access_documents(
        self,
    ):
        docente = User.objects.create_user(
            username="document_permission_docente",
            password="MilalDocumentAcceptance123!",
        )

        docente_group = Group.objects.get(
            name="DOCENTE"
        )
        docente.groups.add(
            docente_group
        )

        StudentProfessionalAssignment.objects.create(
            student=self.student,
            professional=docente,
            professional_role="DOCENTE",
            assigned_by=self.responsible,
        )

        docente_group.permissions.remove(
            Permission.objects.get(
                codename="view_academic_followups"
            )
        )

        self.client.force_authenticate(
            user=docente
        )

        response = self.client.get(
            (
                f"{self.documents_url()}"
                "?context=DOCENTE"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
