from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver"])
class HU01AcceptanceTests(APITestCase):
    """
    Pruebas de aceptación de HU-01:
    Gestión de usuarios y roles.
    """

    def setUp(self):
        self.administrator = User.objects.create_user(
            username="administrador_hu01",
            password="AdministradorSeguro123!",
        )

        self.administrator.groups.add(
            Group.objects.get(name="ADMINISTRADOR")
        )

        self.client.force_authenticate(
            user=self.administrator
        )

    def test_ca_01_administrator_can_register_users(self):
        """
        CA-01:
        El administrador puede registrar usuarios.
        """
        response = self.client.post(
            reverse("user-list"),
            {
                "username": "usuario_registrado",
                "email": "registrado@milal.org.gt",
                "first_name": "Usuario",
                "last_name": "Registrado",
                "password": "RegistroSeguro123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            username="usuario_registrado"
        )

        self.assertTrue(
            user.check_password("RegistroSeguro123!")
        )

        self.assertNotIn(
            "password",
            response.data,
        )

    def test_ca_02_administrator_can_modify_users(self):
        """
        CA-02:
        El administrador puede modificar usuarios.
        """
        target = User.objects.create_user(
            username="usuario_modificable",
            password="ModificarSeguro123!",
            first_name="Original",
            email="original@milal.org.gt",
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[target.id],
            ),
            {
                "first_name": "Modificado",
                "email": "modificado@milal.org.gt",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        self.assertEqual(
            target.first_name,
            "Modificado",
        )

        self.assertEqual(
            target.email,
            "modificado@milal.org.gt",
        )

    def test_ca_03_administrator_can_assign_roles(self):
        """
        CA-03:
        El administrador puede asignar roles.
        """
        target = User.objects.create_user(
            username="usuario_con_roles",
            password="RolesSeguro123!",
        )

        response = self.client.patch(
            reverse(
                "user-roles",
                args=[target.id],
            ),
            {
                "roles": [
                    "DOCENTE",
                    "PSICOLOGO",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        roles = set(
            target.groups.values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            roles,
            {
                "DOCENTE",
                "PSICOLOGO",
            },
        )

    def test_ca_04_system_controls_access_by_role(self):
        """
        CA-04:
        El sistema controla el acceso según el rol.
        """
        docente = User.objects.create_user(
            username="docente_hu01",
            password="DocenteSeguro123!",
        )

        docente.groups.add(
            Group.objects.get(name="DOCENTE")
        )

        self.client.force_authenticate(
            user=docente
        )

        denied_response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            denied_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(
            user=self.administrator
        )

        allowed_response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            allowed_response.status_code,
            status.HTTP_200_OK,
        )

    def test_ca_05_user_cannot_access_functions_outside_role(self):
        """
        CA-05:
        Un usuario no puede acceder a funciones
        que no corresponden a su rol.
        """
        terapeuta = User.objects.create_user(
            username="terapeuta_hu01",
            password="TerapeutaSeguro123!",
        )

        terapeuta.groups.add(
            Group.objects.get(name="TERAPEUTA")
        )

        target = User.objects.create_user(
            username="usuario_protegido",
            password="ProtegidoSeguro123!",
            first_name="Original",
        )

        self.client.force_authenticate(
            user=terapeuta
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[target.id],
            ),
            {
                "first_name": "Cambio no permitido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        target.refresh_from_db()

        self.assertEqual(
            target.first_name,
            "Original",
        )

    def test_ca_06_administrator_can_activate_and_deactivate_users(self):
        """
        CA-06:
        El administrador puede activar y desactivar usuarios.
        """
        target = User.objects.create_user(
            username="usuario_estado_hu01",
            password="EstadoSeguro123!",
        )

        deactivate_response = self.client.patch(
            reverse(
                "user-deactivate",
                args=[target.id],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            deactivate_response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        self.assertFalse(target.is_active)

        activate_response = self.client.patch(
            reverse(
                "user-activate",
                args=[target.id],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            activate_response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        self.assertTrue(target.is_active)