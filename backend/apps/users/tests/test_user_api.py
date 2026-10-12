from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group


User = get_user_model()

@override_settings(ALLOWED_HOSTS=["testserver"])
class UserAPITests(APITestCase):
    """
    Pruebas de regresión para la gestión básica
    de usuarios correspondiente a TASK-03.
    """

    def setUp(self):
        self.authenticated_user = User.objects.create_user(
            username="authenticated_tester",
            password="TesterSeguro123!",
        )

        administrator_role = Group.objects.get(
            name="ADMINISTRADOR"
        )

        self.authenticated_user.groups.add(
            administrator_role
        )

        self.client.force_authenticate(
            user=self.authenticated_user
        )

    def test_create_user(self):
        response = self.client.post(
            reverse("user-list"),
            {
                "username": "nuevo_usuario",
                "email": "nuevo.usuario@milal.org.gt",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "password": "ClaveSegura123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertNotIn("password", response.data)

        user = User.objects.get(
            username="nuevo_usuario"
        )

        self.assertTrue(
            user.check_password("ClaveSegura123!")
        )

    def test_list_users(self):
        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_retrieve_user(self):
        target = User.objects.create_user(
            username="usuario_consulta",
            password="ConsultaSegura123!",
        )

        response = self.client.get(
            reverse(
                "user-detail",
                args=[target.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "usuario_consulta",
        )

    def test_partial_update_user(self):
        target = User.objects.create_user(
            username="usuario_modificar",
            password="ModificarSegura123!",
        )

        response = self.client.patch(
            reverse(
                "user-detail",
                args=[target.id],
            ),
            {
                "first_name": "Nombre Modificado",
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
            "Nombre Modificado",
        )

        self.assertEqual(
            target.email,
            "modificado@milal.org.gt",
        )

    def test_delete_user_is_not_allowed(self):
        target = User.objects.create_user(
            username="usuario_no_eliminar",
            password="NoEliminar123!",
        )

        response = self.client.delete(
            reverse(
                "user-detail",
                args=[target.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            User.objects.filter(
                id=target.id
            ).exists()
        )

    def test_deactivate_user(self):
        target = User.objects.create_user(
            username="usuario_desactivar",
            password="Desactivar123!",
        )

        response = self.client.patch(
            reverse(
                "user-deactivate",
                args=[target.id],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        self.assertFalse(target.is_active)

    def test_activate_user(self):
        target = User.objects.create_user(
            username="usuario_activar",
            password="ActivarSeguro123!",
            is_active=False,
        )

        response = self.client.patch(
            reverse(
                "user-activate",
                args=[target.id],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        target.refresh_from_db()

        self.assertTrue(target.is_active)

    def test_anonymous_user_cannot_access_users(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_password_is_required_when_creating_user(self):
        response = self.client.post(
            reverse("user-list"),
            {
                "username": "sin_password",
                "email": "sin.password@milal.org.gt",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password",
            response.data,
        )

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            reverse("user-list"),
            {
                "username": "password_debil",
                "email": "debil@milal.org.gt",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password",
            response.data,
        )

@override_settings(ALLOWED_HOSTS=["testserver"])
class UserRoleAssignmentAPITests(APITestCase):
    """
    Pruebas de regresión para la asignación de roles
    correspondiente a TASK-04.
    """

    def setUp(self):
        self.authenticated_user = User.objects.create_user(
            username="role_api_tester",
            password="TesterSeguro123!",
        )

        administrator_role = Group.objects.get(
            name="ADMINISTRADOR"
        )

        self.authenticated_user.groups.add(
        administrator_role
        )

        self.target_user = User.objects.create_user(
            username="usuario_roles_test",
            password="RolesSeguro123!",
        )

        self.client.force_authenticate(
            user=self.authenticated_user
        )

    def test_initial_institutional_roles_exist(self):
        expected_roles = {
            "ADMINISTRADOR",
            "DOCENTE",
            "PSICOLOGO",
            "TERAPEUTA",
            "RESPONSABLE_INSTITUCIONAL",
        }

        existing_roles = set(
            Group.objects.values_list(
                "name",
                flat=True,
            )
        )

        self.assertTrue(
            expected_roles.issubset(existing_roles)
        )

    def test_assign_multiple_roles_to_user(self):
        response = self.client.patch(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            ),
            {
                "roles": [
                    "DOCENTE",
                    "TERAPEUTA",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.target_user.refresh_from_db()

        roles = set(
            self.target_user.groups.values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            roles,
            {"DOCENTE", "TERAPEUTA"},
        )

    def test_get_user_roles(self):
        self.target_user.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="PSICOLOGO"),
        )

        response = self.client.get(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            set(response.data["roles"]),
            {"DOCENTE", "PSICOLOGO"},
        )

    def test_replace_existing_roles(self):
        self.target_user.groups.add(
            Group.objects.get(name="DOCENTE"),
            Group.objects.get(name="TERAPEUTA"),
        )

        response = self.client.patch(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            ),
            {
                "roles": [
                    "PSICOLOGO",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.target_user.refresh_from_db()

        roles = list(
            self.target_user.groups.values_list(
                "name",
                flat=True,
            )
        )

        self.assertEqual(
            roles,
            ["PSICOLOGO"],
        )

    def test_invalid_role_is_rejected(self):
        response = self.client.patch(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            ),
            {
                "roles": [
                    "SUPER_ADMIN_INVENTADO",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            self.target_user.groups.count(),
            0,
        )

    def test_duplicate_roles_are_rejected(self):
        response = self.client.patch(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            ),
            {
                "roles": [
                    "DOCENTE",
                    "DOCENTE",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            self.target_user.groups.count(),
            0,
        )

    def test_roles_can_be_cleared(self):
        self.target_user.groups.add(
            Group.objects.get(name="DOCENTE")
        )

        response = self.client.patch(
            reverse(
                "user-roles",
                args=[self.target_user.id],
            ),
            {
                "roles": []
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.target_user.refresh_from_db()

        self.assertEqual(
            self.target_user.groups.count(),
            0,
        )

@override_settings(ALLOWED_HOSTS=["testserver"])
class UserRolePermissionTests(APITestCase):
    """
    Pruebas de autorización por rol para TASK-05.
    """

    NON_ADMIN_ROLES = (
        "DOCENTE",
        "PSICOLOGO",
        "TERAPEUTA",
        "RESPONSABLE_INSTITUCIONAL",
    )

    def create_user_with_role(self, username, role_name):
        user = User.objects.create_user(
            username=username,
            password="PermisoSeguro123!",
        )

        user.groups.add(
            Group.objects.get(name=role_name)
        )

        return user

    def test_user_without_role_cannot_list_users(self):
        user = User.objects.create_user(
            username="usuario_sin_rol",
            password="SinRolSeguro123!",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_non_administrator_roles_cannot_list_users(self):
        for role_name in self.NON_ADMIN_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"list_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                response = self.client.get(
                    reverse("user-list")
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_non_administrator_roles_cannot_create_users(self):
        for role_name in self.NON_ADMIN_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"create_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                response = self.client.post(
                    reverse("user-list"),
                    {
                        "username": f"nuevo_{role_name.lower()}",
                        "password": "NuevoSeguro123!",
                    },
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                self.assertFalse(
                    User.objects.filter(
                        username=f"nuevo_{role_name.lower()}"
                    ).exists()
                )

    def test_non_administrator_roles_cannot_modify_user(self):
        target = User.objects.create_user(
            username="objetivo_modificacion",
            password="ObjetivoSeguro123!",
            first_name="Original",
        )

        for role_name in self.NON_ADMIN_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"modify_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                response = self.client.patch(
                    reverse(
                        "user-detail",
                        args=[target.id],
                    ),
                    {
                        "first_name": "Modificado",
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

    def test_non_administrator_roles_cannot_change_user_status(self):
        active_target = User.objects.create_user(
            username="objetivo_desactivar",
            password="ObjetivoSeguro123!",
        )

        inactive_target = User.objects.create_user(
            username="objetivo_activar",
            password="ObjetivoSeguro123!",
            is_active=False,
        )

        for role_name in self.NON_ADMIN_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"status_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                deactivate_response = self.client.patch(
                    reverse(
                        "user-deactivate",
                        args=[active_target.id],
                    ),
                    {},
                    format="json",
                )

                activate_response = self.client.patch(
                    reverse(
                        "user-activate",
                        args=[inactive_target.id],
                    ),
                    {},
                    format="json",
                )

                self.assertEqual(
                    deactivate_response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                self.assertEqual(
                    activate_response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                active_target.refresh_from_db()
                inactive_target.refresh_from_db()

                self.assertTrue(active_target.is_active)
                self.assertFalse(inactive_target.is_active)

    def test_non_administrator_roles_cannot_assign_roles(self):
        target = User.objects.create_user(
            username="objetivo_roles",
            password="ObjetivoSeguro123!",
        )

        for role_name in self.NON_ADMIN_ROLES:
            with self.subTest(role=role_name):
                user = self.create_user_with_role(
                    username=f"roles_{role_name.lower()}",
                    role_name=role_name,
                )

                self.client.force_authenticate(user=user)

                response = self.client.patch(
                    reverse(
                        "user-roles",
                        args=[target.id],
                    ),
                    {
                        "roles": ["PSICOLOGO"]
                    },
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

                self.assertEqual(
                    target.groups.count(),
                    0,
                )

    def test_inactive_administrator_cannot_access_user_management(self):
        administrator = self.create_user_with_role(
            username="administrador_inactivo",
            role_name="ADMINISTRADOR",
        )

        administrator.is_active = False
        administrator.save(update_fields=["is_active"])

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.get(
            reverse("user-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_administrator_cannot_deactivate_self(self):
        administrator = self.create_user_with_role(
            username="administrador_autodesactivar",
            role_name="ADMINISTRADOR",
        )

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.patch(
            reverse(
                "user-deactivate",
                args=[administrator.id],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        administrator.refresh_from_db()

        self.assertTrue(administrator.is_active)


    def test_administrator_cannot_remove_own_administrator_role(self):
        administrator = self.create_user_with_role(
            username="administrador_autorol",
            role_name="ADMINISTRADOR",
        )

        self.client.force_authenticate(
            user=administrator
        )

        response = self.client.patch(
            reverse(
                "user-roles",
                args=[administrator.id],
            ),
            {
                "roles": [
                    "DOCENTE",
                ]
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        administrator.refresh_from_db()

        roles = set(
            administrator.groups.values_list(
                "name",
                flat=True,
            )
        )

        self.assertIn(
            "ADMINISTRADOR",
            roles,
        )