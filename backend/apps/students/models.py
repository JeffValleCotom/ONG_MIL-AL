from django.db import models


class Student(models.Model):
    institutional_code = models.CharField(
        max_length=30,
        unique=True,
    )
    first_name = models.CharField(
        max_length=100,
    )
    last_name = models.CharField(
        max_length=100,
    )
    date_of_birth = models.DateField()
    admission_date = models.DateField()
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.institutional_code} - "
            f"{self.first_name} {self.last_name}"
        )