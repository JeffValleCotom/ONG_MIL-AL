from dataclasses import dataclass
from pathlib import Path
import zipfile


MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024

CANONICAL_MIME_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
}

ALLOWED_DECLARED_MIME_BY_EXTENSION = {
    ".pdf": {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    },
    ".jpg": {
        "image/jpeg",
        "image/jpg",
        "image/pjpeg",
        "application/octet-stream",
    },
    ".jpeg": {
        "image/jpeg",
        "image/jpg",
        "image/pjpeg",
        "application/octet-stream",
    },
    ".png": {
        "image/png",
        "application/octet-stream",
    },
    ".docx": {
        (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "application/zip",
        "application/octet-stream",
    },
}


class DocumentValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class DocumentValidationResult:
    original_filename: str
    extension: str
    mime_type: str
    size_bytes: int


def _get_original_filename(uploaded_file):
    filename = (
        str(uploaded_file.name)
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
        .strip()
    )

    if not filename or "\x00" in filename:
        raise DocumentValidationError(
            "El archivo debe poseer un nombre válido."
        )

    if len(filename) > 255:
        raise DocumentValidationError(
            "El nombre del archivo no puede exceder "
            "255 caracteres."
        )

    return filename


def _get_extension(filename):
    extension = Path(filename).suffix.lower()

    if not extension:
        raise DocumentValidationError(
            "El archivo debe poseer una extensión."
        )

    if extension not in CANONICAL_MIME_BY_EXTENSION:
        raise DocumentValidationError(
            "Formato de archivo no permitido. "
            "Se admiten PDF, JPEG, PNG y DOCX."
        )

    return extension


def _get_size(uploaded_file):
    try:
        size = int(uploaded_file.size)
    except (TypeError, ValueError, AttributeError):
        raise DocumentValidationError(
            "No fue posible determinar el tamaño "
            "del archivo."
        )

    if size <= 0:
        raise DocumentValidationError(
            "El archivo no puede estar vacío."
        )

    if size > MAX_DOCUMENT_SIZE_BYTES:
        raise DocumentValidationError(
            "El archivo no puede superar 10 MiB."
        )

    return size


def _get_declared_mime(uploaded_file):
    declared_mime = (
        getattr(uploaded_file, "content_type", "")
        or "application/octet-stream"
    )

    declared_mime = (
        str(declared_mime)
        .split(";", 1)[0]
        .strip()
        .lower()
    )

    return (
        declared_mime
        or "application/octet-stream"
    )


def _validate_declared_mime(
    extension,
    declared_mime,
):
    allowed_mime_types = (
        ALLOWED_DECLARED_MIME_BY_EXTENSION[
            extension
        ]
    )

    if declared_mime not in allowed_mime_types:
        raise DocumentValidationError(
            "El tipo MIME declarado no coincide "
            "con el formato del archivo."
        )


def _is_pdf(uploaded_file):
    uploaded_file.seek(0)
    return uploaded_file.read(5) == b"%PDF-"


def _is_jpeg(uploaded_file, size):
    if size < 4:
        return False

    uploaded_file.seek(0)

    if uploaded_file.read(3) != b"\xff\xd8\xff":
        return False

    uploaded_file.seek(-2, 2)

    return uploaded_file.read(2) == b"\xff\xd9"


def _is_png(uploaded_file):
    uploaded_file.seek(0)
    header = uploaded_file.read(16)

    return (
        len(header) >= 16
        and header[:8]
        == b"\x89PNG\r\n\x1a\n"
        and header[12:16] == b"IHDR"
    )


def _is_docx(uploaded_file):
    uploaded_file.seek(0)

    if not zipfile.is_zipfile(uploaded_file):
        return False

    uploaded_file.seek(0)

    try:
        with zipfile.ZipFile(
            uploaded_file,
            mode="r",
        ) as archive:
            names = set(archive.namelist())
    except (
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
        OSError,
    ):
        return False

    required_entries = {
        "[Content_Types].xml",
        "word/document.xml",
    }

    return required_entries.issubset(names)


def _content_matches_extension(
    uploaded_file,
    extension,
    size,
):
    if extension == ".pdf":
        return _is_pdf(uploaded_file)

    if extension in {".jpg", ".jpeg"}:
        return _is_jpeg(uploaded_file, size)

    if extension == ".png":
        return _is_png(uploaded_file)

    if extension == ".docx":
        return _is_docx(uploaded_file)

    return False


def validate_uploaded_document(uploaded_file):
    original_filename = _get_original_filename(
        uploaded_file
    )

    extension = _get_extension(
        original_filename
    )

    size = _get_size(uploaded_file)

    declared_mime = _get_declared_mime(
        uploaded_file
    )

    _validate_declared_mime(
        extension,
        declared_mime,
    )

    try:
        content_is_valid = (
            _content_matches_extension(
                uploaded_file,
                extension,
                size,
            )
        )
    finally:
        uploaded_file.seek(0)

    if not content_is_valid:
        raise DocumentValidationError(
            "El contenido del archivo no coincide "
            "con un formato permitido."
        )

    return DocumentValidationResult(
        original_filename=original_filename,
        extension=extension,
        mime_type=(
            CANONICAL_MIME_BY_EXTENSION[
                extension
            ]
        ),
        size_bytes=size,
    )
