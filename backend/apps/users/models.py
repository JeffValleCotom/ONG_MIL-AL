from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Usuario institucional de la plataforma MIL-AL.

    Se extiende AbstractUser para conservar el sistema robusto de
    autenticación y permisos proporcionado por Django y permitir
    futuras ampliaciones sin sustituir el modelo de usuario.
    """

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username