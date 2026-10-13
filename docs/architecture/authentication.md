# Diseño del proceso de autenticación

## HU-02 - Autenticación de usuarios

La plataforma MIL-AL utilizará autenticación basada en sesiones
de Django para identificar a los usuarios institucionales.

## Objetivo

Permitir que un usuario institucional pueda iniciar sesión,
mantener una sesión autenticada, consultar su identidad actual
y cerrar sesión de forma segura.

## Arquitectura

El frontend React se comunica exclusivamente con la API REST
de Django.

React no accede directamente a SQL Server ni almacena las
credenciales del usuario.

Flujo general:

1. React solicita un token CSRF a Django.
2. El usuario ingresa nombre de usuario y contraseña.
3. React envía las credenciales al endpoint de inicio de sesión.
4. Django valida las credenciales mediante authenticate().
5. Si son válidas, Django crea la sesión mediante login().
6. Django mantiene la sesión mediante su sistema de sesiones.
7. El navegador conserva la cookie de sesión.
8. Las solicitudes posteriores reutilizan esa sesión.
9. Django continúa verificando roles y permisos.
10. Al cerrar sesión, Django invalida la sesión mediante logout().

## Endpoints previstos

### GET /api/v1/auth/csrf/

Obtiene o establece el token CSRF requerido para solicitudes
que modifican información.

### POST /api/v1/auth/login/

Recibe:

- username
- password

Responsabilidades:

- validar credenciales;
- rechazar credenciales incorrectas;
- impedir autenticación de usuarios inactivos;
- crear una sesión válida;
- devolver información básica del usuario;
- devolver sus roles institucionales.

### GET /api/v1/auth/session/

Responsabilidades:

- comprobar si existe una sesión válida;
- devolver el usuario autenticado;
- devolver sus roles;
- permitir que React restaure el estado de autenticación
  después de recargar la aplicación.

### POST /api/v1/auth/logout/

Responsabilidades:

- cerrar la sesión actual;
- invalidar la autenticación del usuario.

## Seguridad

- Las contraseñas nunca se almacenan en React.
- Django valida las credenciales mediante authenticate().
- La cookie de sesión será HttpOnly.
- Las operaciones que modifican datos utilizarán protección CSRF.
- Los usuarios inactivos no podrán autenticarse.
- React no será responsable de la autorización definitiva.
- Django continuará verificando roles y permisos.
- No se almacenarán contraseñas ni identificadores de sesión
  en localStorage.

## Roles y autenticación

La autenticación responde:

¿Quién es el usuario?

La autorización responde:

¿Qué puede hacer el usuario?

Los roles institucionales existentes son:

- ADMINISTRADOR
- DOCENTE
- PSICOLOGO
- TERAPEUTA
- RESPONSABLE_INSTITUCIONAL

Una vez autenticado, Django devolverá los roles asignados al usuario.
React podrá utilizarlos para adaptar la interfaz, pero la autorización
real continuará siendo responsabilidad del backend.

## Persistencia de sesión

La sesión se gestionará mediante el sistema estándar de sesiones
de Django y la tabla django_session existente en SQL Server.

Durante desarrollo, React utilizará el proxy de Vite para acceder
a la API mediante /api.

La configuración definitiva de seguridad de cookies se ajustará
durante la preparación del despliegue.

## Responsabilidades por Task

TASK-07:
Diseñar el proceso de autenticación.

TASK-08:
Implementar formulario de inicio de sesión.

TASK-09:
Implementar validación de credenciales.

TASK-10:
Implementar gestión de sesiones.

TASK-11:
Implementar cierre de sesión.

TASK-12:
Realizar pruebas de autenticación.