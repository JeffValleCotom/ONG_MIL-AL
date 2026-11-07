from pathlib import Path
from tempfile import SpooledTemporaryFile

from django.conf import settings
from django.core.files import File
from django.core.files.storage import (
    FileSystemStorage,
    Storage,
)
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateStudentDocumentStorage(Storage):
    """
    Storage privado para documentos de estudiantes.

    Desarrollo local:
        backend/private_media/

    Producción:
        contenedor privado de Azure Blob Storage.

    Los archivos nunca exponen una URL pública.
    """

    def __init__(self):
        self._local_storage = None
        self._blob_service_client = None
        self._container_client = None

    @property
    def uses_azure(self):
        return settings.AZURE_STORAGE_ENABLED

    @property
    def local_storage(self):
        if self._local_storage is None:
            self._local_storage = FileSystemStorage(
                location=settings.PRIVATE_MEDIA_ROOT,
            )

        return self._local_storage

    @property
    def blob_service_client(self):
        if self._blob_service_client is None:
            from azure.identity import (
                DefaultAzureCredential,
            )
            from azure.storage.blob import (
                BlobServiceClient,
            )

            account_url = (
                "https://"
                f"{settings.AZURE_STORAGE_ACCOUNT_NAME}"
                ".blob.core.windows.net"
            )

            credential = DefaultAzureCredential()

            self._blob_service_client = (
                BlobServiceClient(
                    account_url=account_url,
                    credential=credential,
                )
            )

        return self._blob_service_client

    @property
    def container_client(self):
        if self._container_client is None:
            self._container_client = (
                self.blob_service_client
                .get_container_client(
                    settings
                    .AZURE_STORAGE_PRIVATE_CONTAINER
                )
            )

        return self._container_client

    def _open(self, name, mode="rb"):
        if not self.uses_azure:
            return self.local_storage.open(
                name,
                mode,
            )

        if mode not in {"rb", "r"}:
            raise ValueError(
                "Los documentos privados solo "
                "pueden abrirse en modo lectura."
            )

        downloader = (
            self.container_client
            .download_blob(name)
        )

        temporary_file = SpooledTemporaryFile(
            max_size=(
                settings
                .AZURE_STORAGE_MAX_MEMORY_SIZE
            ),
            mode="w+b",
        )

        downloader.readinto(
            temporary_file
        )

        temporary_file.seek(0)

        return File(
            temporary_file,
            name=Path(name).name,
        )

    def _save(self, name, content):
        if not self.uses_azure:
            return self.local_storage.save(
                name,
                content,
            )

        if hasattr(content, "seek"):
            content.seek(0)

        self.container_client.upload_blob(
            name=name,
            data=content,
            overwrite=False,
        )

        return name

    def exists(self, name):
        if not self.uses_azure:
            return self.local_storage.exists(
                name
            )

        blob_client = (
            self.container_client
            .get_blob_client(name)
        )

        return blob_client.exists()

    def delete(self, name):
        if not name:
            return

        if not self.uses_azure:
            self.local_storage.delete(name)
            return

        from azure.core.exceptions import (
            ResourceNotFoundError,
        )

        blob_client = (
            self.container_client
            .get_blob_client(name)
        )

        try:
            blob_client.delete_blob(
                delete_snapshots="include",
            )
        except ResourceNotFoundError:
            pass

    def size(self, name):
        if not self.uses_azure:
            return self.local_storage.size(
                name
            )

        properties = (
            self.container_client
            .get_blob_client(name)
            .get_blob_properties()
        )

        return properties.size

    def get_modified_time(self, name):
        if not self.uses_azure:
            return (
                self.local_storage
                .get_modified_time(name)
            )

        properties = (
            self.container_client
            .get_blob_client(name)
            .get_blob_properties()
        )

        return properties.last_modified

    def url(self, name):
        raise NotImplementedError(
            "Los documentos privados no "
            "exponen URLs públicas."
        )


private_student_document_storage = (
    PrivateStudentDocumentStorage()
)
