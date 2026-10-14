# Diseño de la estructura del perfil de usuario

## HU-03 - Gestión de perfiles de usuario

La plataforma MIL-AL permitirá que cada usuario institucional
autenticado consulte y actualice la información permitida de
su propio perfil.

El perfil utilizará la información existente en el modelo User
de Django. No se creará una tabla adicional de perfiles mientras
los requerimientos puedan ser cubiertos por el modelo actual.

## Objetivo

Permitir que un usuario autenticado pueda consultar su propia
información institucional y actualizar únicamente los datos
personales autorizados, manteniendo protegidos los campos
relacionados con identidad, roles, permisos y seguridad.

## Arquitectura

El frontend React se comunicará exclusivamente con la API REST
de Django.

El perfil siempre estará asociado al usuario autenticado mediante:

request.user

El frontend no enviará un identificador de usuario para consultar
o modificar el perfil propio.

Flujo general:

1. El usuario inicia sesión en la plataforma.
2. React solicita el perfil actual a Django.
3. Django obtiene el usuario desde request.user.
4. Django devuelve únicamente la información autorizada.
5. El usuario modifica los campos permitidos.
6. React envía únicamente los datos modificables.
7. Django valida la información recibida.
8. Django rechaza cualquier intento de modificar datos restringidos.
9. Los cambios válidos se almacenan en SQL Server.

## Estructura del perfil

### Datos consultables

El usuario podrá consultar:

- id
- username
- email
- first_name
- last_name
- roles
- is_active
- date_joined
- last_login

### Datos editables

El propio usuario podrá modificar:

- email
- first_name
- last_name

### Datos restringidos

El usuario no podrá modificar desde la gestión de su perfil:

- id
- username
- roles
- groups
- is_active
- is_staff
- is_superuser
- date_joined
- last_login
- password

La modificación de roles, estado y permisos corresponde a los
procesos administrativos de gestión de usuarios.

El cambio de contraseña se considera un proceso de seguridad
independiente y no forma parte del alcance actual de HU-03.

## Endpoints previstos

### GET /api/v1/profile/

Responsabilidades:

- requerir una sesión autenticada;
- identificar al usuario mediante request.user;
- devolver la información de su propio perfil;
- devolver sus roles institucionales;
- impedir la consulta de perfiles de otros usuarios mediante
  identificadores proporcionados por el cliente.

Respuesta prevista:

```json
{
  "id": 9,
  "username": "admin_demo",
  "email": "admin.demo@milal.local",
  "first_name": "Administrador",
  "last_name": "Demo",
  "roles": [
    "ADMINISTRADOR"
  ],
  "is_active": true,
  "date_joined": "2026-10-14T00:00:00Z",
  "last_login": "2026-10-14T00:00:00Z"
}