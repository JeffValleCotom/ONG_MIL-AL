# Matriz de permisos de acceso

## 1. Objetivo

Definir la matriz de autorización basada en roles de la plataforma MIL-AL.

La matriz establece qué funcionalidades puede utilizar cada rol institucional
y servirá como contrato para la implementación de permisos en el backend.

La autorización debe aplicarse en el servidor. La interfaz React puede ocultar
o deshabilitar opciones por experiencia de usuario, pero no constituye un
mecanismo de seguridad.

## 2. Modelo de autorización

La plataforma utiliza un esquema RBAC (Role-Based Access Control).

En Django:

- Los usuarios se representan mediante el modelo `User`.
- Los roles institucionales se representan mediante `Group`.
- Los permisos se representarán mediante `Permission`.
- Un usuario puede pertenecer técnicamente a más de un grupo.
- Los permisos efectivos del usuario serán derivados de sus roles.

La asignación de permisos debe seguir el principio de mínimo privilegio.

Tener el rol `ADMINISTRADOR` no implica acceso automático a información
académica, psicológica o terapéutica sensible.

## 3. Roles institucionales

Los roles definidos actualmente son:

- `ADMINISTRADOR`
- `DOCENTE`
- `PSICOLOGO`
- `TERAPEUTA`
- `RESPONSABLE_INSTITUCIONAL`

## 4. Catálogo conceptual de permisos

| Código conceptual | Funcionalidad protegida |
|---|---|
| `manage_users` | Crear, consultar, editar, activar y desactivar usuarios institucionales |
| `manage_roles` | Asignar y retirar roles institucionales |
| `manage_permissions` | Administrar la asociación de permisos a roles |
| `view_students` | Consultar información general de estudiantes |
| `manage_students` | Crear y actualizar información general de estudiantes |
| `manage_student_assignments` | Administrar asignaciones de profesionales a estudiantes |
| `view_academic_followups` | Consultar seguimientos académicos |
| `manage_academic_followups` | Registrar y actualizar seguimientos académicos |
| `view_psychological_followups` | Consultar seguimientos psicológicos |
| `manage_psychological_followups` | Registrar y actualizar seguimientos psicológicos |
| `view_therapy_followups` | Consultar seguimientos terapéuticos |
| `manage_therapy_followups` | Registrar y actualizar seguimientos terapéuticos |
| `view_interventions` | Consultar intervenciones o atenciones interdisciplinarias |
| `manage_interventions` | Registrar y actualizar intervenciones |
| `view_reports` | Consultar reportes autorizados |
| `view_dashboard` | Consultar indicadores y paneles autorizados |
| `view_alerts` | Consultar alertas correspondientes al ámbito del usuario |
| `use_ai_assistant` | Utilizar funcionalidades de asistencia mediante IA |
| `view_audit` | Consultar información de auditoría y trazabilidad |

## 5. Matriz Rol × Permiso

Leyenda:

- `X`: permiso concedido.
- `—`: permiso no concedido.

| Permiso | Administrador | Docente | Psicólogo | Terapeuta | Responsable institucional |
|---|:---:|:---:|:---:|:---:|:---:|
| `manage_users` | X | — | — | — | — |
| `manage_roles` | X | — | — | — | — |
| `manage_permissions` | X | — | — | — | — |
| `view_students` | — | X | X | X | X |
| `manage_students` | — | — | — | — | X |
| `manage_student_assignments` | — | — | — | — | X |
| `view_academic_followups` | — | X | — | — | — |
| `manage_academic_followups` | — | X | — | — | — |
| `view_psychological_followups` | — | — | X | — | — |
| `manage_psychological_followups` | — | — | X | — | — |
| `view_therapy_followups` | — | — | — | X | — |
| `manage_therapy_followups` | — | — | — | X | — |
| `view_interventions` | — | — | X | X | — |
| `manage_interventions` | — | — | X | X | — |
| `view_reports` | — | X | X | X | X |
| `view_dashboard` | — | X | X | X | X |
| `view_alerts` | — | X | X | X | X |
| `use_ai_assistant` | — | X | X | X | — |
| `view_audit` | X | — | — | — | — |

## 6. Reglas de autorización

La existencia de un permiso habilita una funcionalidad, pero no implica
acceso irrestricto a todos los registros almacenados por la plataforma.

Cuando una funcionalidad maneje información sensible, podrán aplicarse además
reglas de alcance de datos según el rol y el contexto del usuario.

Por ejemplo, el permiso `view_alerts` permite acceder a la funcionalidad de
alertas, pero la información retornada deberá limitarse a las alertas que el
rol esté autorizado a conocer.

Los permisos deben comprobarse siempre en el backend antes de ejecutar una
operación protegida.

Una respuesta proveniente de React no debe utilizarse como evidencia de que
un usuario posee autorización.

### Alcance por asignación de estudiantes

A partir de HU-07, el permiso `view_students` habilita la funcionalidad de
consulta, pero no implica acceso a todos los estudiantes de la institución.

Para los roles profesionales:

- `DOCENTE` solo podrá consultar estudiantes con una asignación activa bajo el
  contexto `DOCENTE`;
- `PSICOLOGO` solo podrá consultar estudiantes con una asignación activa bajo el
  contexto `PSICOLOGO`;
- `TERAPEUTA` solo podrá consultar estudiantes con una asignación activa bajo el
  contexto `TERAPEUTA`.

El rol `RESPONSABLE_INSTITUCIONAL` conservará el alcance institucional necesario
para gestionar información general y asignaciones.

La posesión simultánea de varios roles no combinará las asignaciones entre
contextos profesionales.

Por ejemplo, una asignación como `DOCENTE` no habilitará el acceso psicológico
del mismo estudiante aunque el usuario también posea el rol `PSICOLOGO`.

El backend deberá aplicar estas restricciones antes de retornar información al
frontend.

### Reglas generales

- La autorización utiliza una política de denegación por defecto: si un usuario
  no posee explícitamente el permiso requerido, el acceso debe ser rechazado.

- Si un usuario pertenece a más de un rol institucional, sus permisos efectivos
  corresponden a la unión de los permisos concedidos a esos roles.

- La posesión de un permiso no elimina las restricciones de alcance sobre los
  datos. Un usuario puede tener acceso a una funcionalidad y, al mismo tiempo,
  estar limitado a determinados registros según su rol y contexto.

- Los usuarios inactivos no deben poder ejecutar funcionalidades protegidas.

- El superusuario técnico de Django no se considera un rol institucional.
  `ADMINISTRADOR` continúa siendo un rol funcional independiente de
  `is_superuser`.

## 7. Perfil propio

Las operaciones sobre el perfil personal implementadas en HU-03 no dependen
de esta matriz de roles.

Todo usuario autenticado puede:

- consultar su propio perfil;
- actualizar los campos permitidos de su propio perfil.

El backend identifica el perfil mediante `request.user`.

Los campos restringidos continúan protegidos independientemente de los roles
del usuario.

## 8. Administración funcional y superusuario de Django

El rol institucional `ADMINISTRADOR` es diferente de `is_superuser`.

La aplicación no debe exigir `is_superuser=True` para administrar usuarios,
roles o permisos institucionales.

La autorización funcional se determinará mediante los roles y permisos
definidos por la plataforma.

## 9. Implementación posterior

Esta matriz es una definición de arquitectura.

TASK-20 implementará el catálogo de permisos.

TASK-21 asociará los permisos con los roles institucionales.

TASK-22 aplicará los permisos a las funcionalidades protegidas.

TASK-23 verificará y restringirá los intentos de acceso no autorizado.

TASK-24 validará el comportamiento mediante pruebas de autorización.