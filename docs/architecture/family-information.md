# Diseño de información familiar del estudiante

## 1. Objetivo

Definir la estructura funcional y técnica para registrar, consultar y actualizar la información familiar asociada a los estudiantes de la ONG MIL-AL.

La información familiar forma parte del expediente individual del estudiante, pero se mantiene como una entidad independiente de `Student` para permitir múltiples familiares por estudiante y conservar una estructura normalizada.

## 2. Alcance

HU-09 permitirá:

- Registrar familiares asociados a un estudiante.
- Consultar la información familiar desde el expediente individual.
- Actualizar la información registrada.
- Identificar un contacto principal del estudiante.
- Desactivar registros sin eliminarlos físicamente.
- Conservar información histórica.
- Aplicar control de acceso según rol, permisos y contexto activo.

No se implementará eliminación física de información familiar.

## 3. Modelo conceptual

La relación será:

`Student 1:N StudentFamilyMember`

Un estudiante puede tener cero, uno o varios familiares registrados.

Cada registro familiar pertenece exclusivamente a un estudiante.

No se implementará una entidad global de personas compartida entre estudiantes. Si una misma persona está relacionada con dos estudiantes, por ejemplo hermanos, se registrará dentro de cada expediente de manera independiente.

Esta decisión evita acoplamiento entre expedientes, simplifica el control de acceso y evita introducir un sistema de identidad familiar que no forma parte del alcance actual.

## 4. Entidad StudentFamilyMember

La entidad propuesta es `StudentFamilyMember`.

### Campos

| Campo | Tipo lógico | Obligatorio | Descripción |
| --- | --- | --- | --- |
| `id` | Identificador | Sí | Identificador interno del registro. |
| `student` | FK → Student | Sí | Estudiante al que pertenece el familiar. |
| `first_name` | Texto, máx. 100 | Sí | Nombres del familiar. |
| `last_name` | Texto, máx. 100 | Sí | Apellidos del familiar. |
| `relationship` | Opción controlada | Sí | Relación con el estudiante. |
| `relationship_detail` | Texto, máx. 100 | Condicional | Descripción cuando `relationship = OTRO`. |
| `phone` | Texto, máx. 30 | No | Número telefónico de contacto. |
| `email` | Correo electrónico | No | Correo electrónico del familiar. |
| `address` | Texto, máx. 255 | No | Dirección de contacto. |
| `is_primary_contact` | Booleano | Sí | Indica si es el contacto principal del estudiante. |
| `is_active` | Booleano | Sí | Indica si el registro familiar continúa vigente. |
| `deactivated_at` | Fecha y hora | No | Momento en que el registro dejó de estar activo. |
| `created_by` | FK → User | Sí | Usuario que registró la información. |
| `updated_by` | FK → User | Sí | Usuario que realizó la última modificación. |
| `created_at` | Fecha y hora | Sí | Fecha de creación. |
| `updated_at` | Fecha y hora | Sí | Fecha de última modificación. |

No se almacenarán documentos de identificación, información médica, fecha de nacimiento u otros datos personales adicionales porque no son necesarios para el alcance de HU-09.

## 5. Tipos de parentesco

`relationship` utilizará un conjunto controlado de valores:

- `MADRE`
- `PADRE`
- `HERMANO_A`
- `ABUELO_A`
- `TIO_A`
- `TUTOR`
- `CUIDADOR`
- `OTRO`

Cuando se seleccione `OTRO`, `relationship_detail` será obligatorio.

Para cualquier otro parentesco, `relationship_detail` deberá permanecer vacío.

## 6. Contacto principal

Un estudiante podrá tener como máximo un familiar activo marcado como `is_primary_contact = True`.

Será válido que temporalmente un estudiante no tenga contacto principal.

La restricción deberá considerar únicamente registros activos.

Cuando un contacto principal sea desactivado, el sistema permitirá que posteriormente otro familiar sea definido como contacto principal.

El término “contacto principal” se utiliza deliberadamente para no confundir esta responsabilidad familiar con el rol funcional `RESPONSABLE_INSTITUCIONAL` de la plataforma.

## 7. Reglas de validación

Los nombres y apellidos deberán eliminar espacios innecesarios antes de almacenarse.

`first_name`, `last_name` y `relationship` son obligatorios.

Si `relationship = OTRO`, deberá existir `relationship_detail`.

Si el parentesco no es `OTRO`, `relationship_detail` no deberá contener información.

El correo electrónico, cuando exista, deberá tener formato válido.

El teléfono se almacenará como texto para soportar prefijos internacionales, símbolos como `+` y distintas formas válidas de numeración.

No se impondrá unicidad sobre nombres, parentesco, teléfono o correo.

Dos familiares pueden compartir nombres y un mismo familiar puede estar asociado a más de un estudiante. Por este motivo, no se utilizará una restricción de identidad basada en datos personales.

La única restricción de unicidad funcional será tener como máximo un contacto principal activo por estudiante.

## 8. Estado e historial

Los registros familiares no se eliminarán físicamente.

La baja de un familiar se representará mediante:

- `is_active = False`
- `deactivated_at` con la fecha y hora correspondiente.

Los registros inactivos permanecerán disponibles para consulta histórica.

La información histórica no deberá desaparecer del expediente.

Un registro desactivado no será considerado contacto principal activo.

## 9. Permisos

La gestión utilizará el catálogo funcional existente.

### RESPONSABLE_INSTITUCIONAL

Con contexto `RESPONSABLE_INSTITUCIONAL`:

- `view_students`: consultar información familiar.
- `manage_students`: registrar, actualizar y desactivar información familiar.

La autorización debe comprobar el permiso dentro del rol/contexto correspondiente y no únicamente la unión global de permisos del usuario.

### DOCENTE, PSICOLOGO y TERAPEUTA

Cuando tengan acceso válido al expediente del estudiante mediante una asignación profesional activa:

- podrán consultar la sección familiar;
- no podrán registrar familiares;
- no podrán actualizar familiares;
- no podrán desactivar familiares.

La información será de solo lectura para estos contextos.

### ADMINISTRADOR

El rol funcional `ADMINISTRADOR` no obtiene acceso automático al expediente individual y, por lo tanto, tampoco obtiene acceso automático a la información familiar.

Ser superusuario de Django tampoco deberá utilizarse como bypass del control funcional establecido para el expediente.

## 10. Usuarios multirrol

La autorización deberá respetar el contexto activo solicitado.

Ejemplo:

Un usuario que posea simultáneamente los roles `RESPONSABLE_INSTITUCIONAL` y `DOCENTE`:

- en contexto `DOCENTE` podrá consultar la información familiar del estudiante asignado, pero no administrarla;
- en contexto `RESPONSABLE_INSTITUCIONAL` podrá administrarla si posee `manage_students`.

React no deberá inferir permisos a partir de la lista de roles.

Django será la autoridad de autorización.

## 11. Integración con el expediente individual

La información familiar se incorporará al endpoint del expediente:

`GET /api/v1/students/{id}/record/`

La respuesta podrá incluir una sección lógica:

`sections.family`

La presencia de la sección será determinada por Django después de validar el acceso al expediente.

React nunca deberá recibir información familiar no autorizada para posteriormente ocultarla visualmente.

Para la gestión se expondrá una capability calculada por backend, por ejemplo:

`capabilities.manage_family`

Esta capability será únicamente una ayuda de experiencia de usuario. Las operaciones de escritura seguirán protegidas independientemente por Django.

## 12. Operaciones previstas

La API deberá soportar posteriormente las siguientes operaciones funcionales:

- Registrar un familiar.
- Consultar familiares activos e históricos.
- Consultar un familiar específico.
- Actualizar parcialmente un familiar mediante `PATCH`.
- Desactivar un familiar.

No se habilitará `DELETE`.

No se requiere `PUT`; las actualizaciones utilizarán `PATCH`, siguiendo el patrón actual de la plataforma.

## 13. Consideraciones para estudiantes inactivos

Un estudiante inactivo podrá conservar y consultar su información familiar histórica.

La información familiar es administrativa y no constituye un nuevo seguimiento académico, psicológico o terapéutico.

Por ello, un Responsable Institucional autorizado podrá corregir o actualizar información familiar de un estudiante inactivo cuando sea necesario para mantener la integridad del expediente.

## 14. Principios de seguridad

La seguridad se aplicará en backend.

Ocultar botones en React no constituye una medida de autorización.

Toda operación deberá verificar:

1. autenticación;
2. usuario activo;
3. contexto solicitado válido;
4. rol correspondiente;
5. permiso funcional requerido;
6. alcance sobre el estudiante;
7. estado y reglas propias del registro familiar.

Las consultas profesionales deberán mantener las reglas existentes de acceso al expediente y asignación activa.

## 15. Decisiones de diseño

Se utiliza una entidad independiente y relacionada uno-a-muchos con `Student`.

No se modifica la tabla `Student` para agregar columnas por cada posible familiar.

No se crea un catálogo global de personas familiares.

No se crean permisos funcionales nuevos porque `view_students` y `manage_students` cubren adecuadamente este subdominio administrativo.

No existe eliminación física.

No se almacena información personal que no sea necesaria para la finalidad de contacto y vínculo familiar.

La autorización continuará siendo contextual y autoritativa en Django.
