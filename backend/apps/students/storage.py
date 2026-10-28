from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateStudentDocumentStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "location",
            settings.PRIVATE_MEDIA_ROOT,
        )
        super().__init__(*args, **kwargs)

    def url(self, name):
        raise NotImplementedError(
            "Los documentos privados no exponen URLs públicas."
        )


private_student_document_storage = PrivateStudentDocumentStorage()
