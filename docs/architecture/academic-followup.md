# Arquitectura del seguimiento académico

## 1. Objetivo

Definir formalmente la arquitectura del seguimiento académico correspondiente a:

- `FEATURE-03 - Seguimiento académico, psicológico y terapéutico`
- `HU-11 - Seguimiento académico`
- `TASK-61 - Diseñar estructura del seguimiento académico`

La finalidad del seguimiento académico es permitir que los docentes autorizados registren, consulten y actualicen información académica de los estudiantes que tengan asignados, manteniendo trazabilidad, separación de responsabilidades y control de acceso desde el backend.

## 2. Trazabilidad con funcionalidades existentes

Parte de la infraestructura requerida por HU-11 fue implementada previamente como dependencia de HU-07, debido a que el expediente integral del estudiante necesitaba incorporar información académica.

HU-11 no introducirá una segunda estructura académica ni duplicará funcionalidades existentes.

La entidad canónica continuará siendo:

`AcademicFollowUp`

Las funcionalidades existentes deberán reutilizarse y validarse contra los requerimientos de HU-11.

Cuando una tarea de HU-11 ya se encuentre completamente satisfecha por una implementación previa, dicha tarea se utilizará para documentar y validar la trazabilidad correspondiente, incorporando únicamente los faltantes que se identifiquen.

## 3. Separación del dominio académico

La información académica no forma parte directamente de la entidad `Student`.

`Student` representa la información general e institucional del estudiante, mientras que los seguimientos académicos se almacenan mediante una entidad independiente relacionada con el estudiante.

Relación conceptual:

```text
Student
  |
  +-- AcademicFollowUp
  +-- AcademicFollowUp
  +-- AcademicFollowUp
```

Un estudiante puede poseer múltiples seguimientos académicos a lo largo del tiempo.

Cada seguimiento pertenece a un único estudiante.

## 4. Entidad AcademicFollowUp

La estructura académica canónica es `AcademicFollowUp`.

Campos definidos:

| Campo | Tipo conceptual | Descripción |
| --- | --- | --- |
| `id` | Identificador | Identificador interno del seguimiento |
| `student` | Relación | Estudiante al que pertenece el seguimiento |
| `followup_date` | Fecha | Fecha en que corresponde el seguimiento |
| `academic_period` | Texto, máximo 50 | Período académico asociado |
| `subject` | Texto, máximo 120 | Asignatura, área o materia relacionada |
| `observations` | Texto | Observaciones académicas principales |
| `strengths` | Texto opcional | Fortalezas identificadas |
| `areas_for_improvement` | Texto opcional | Áreas académicas que requieren mejora |
| `recommendations` | Texto opcional | Recomendaciones derivadas del seguimiento |
| `created_by` | Usuario | Usuario que registró el seguimiento |
| `updated_by` | Usuario | Usuario que realizó la última actualización |
| `created_at` | Fecha y hora | Momento de creación |
| `updated_at` | Fecha y hora | Momento de última modificación |

## 5. Relaciones

### Student

`AcademicFollowUp` mantiene una relación muchos-a-uno con `Student`.

Cada seguimiento académico pertenece a un estudiante y un estudiante puede tener múltiples seguimientos.

La relación utiliza protección frente a eliminación para preservar información histórica.

### Usuario creador

`created_by` identifica al usuario responsable de crear el seguimiento.

Este dato forma parte de la trazabilidad y no debe ser proporcionado libremente por el cliente.

El backend lo obtiene del usuario autenticado.

### Usuario actualizador

`updated_by` identifica al usuario responsable de la última modificación.

El backend actualiza este dato utilizando al usuario autenticado que realiza la operación.

## 6. Ordenamiento e índice

Los seguimientos académicos se ordenan utilizando:

1. `followup_date` descendente;
2. `created_at` descendente;
3. `id` descendente.

Esto permite presentar primero los seguimientos más recientes.

La estructura cuenta con un índice compuesto sobre:

```text
student
followup_date
```

para favorecer consultas de seguimientos por estudiante y fecha.

## 7. Contexto académico

El dominio académico utiliza exclusivamente el contexto:

```text
DOCENTE
```

Una solicitud académica no debe autorizarse únicamente porque el usuario posea una sesión válida.

El backend debe validar conjuntamente:

1. usuario autenticado;
2. contexto `DOCENTE`;
3. pertenencia al rol `DOCENTE`;
4. permiso funcional requerido;
5. asignación profesional activa con el estudiante;
6. alcance del recurso solicitado.

Un usuario con varios roles debe continuar operando bajo el contexto solicitado.

Poseer simultáneamente `DOCENTE` y otro rol no permite combinar permisos o asignaciones de distintos contextos.

## 8. Permisos funcionales

El dominio académico utiliza los permisos:

### view_academic_followups

Permite consultar seguimientos académicos.

Aplica a operaciones de:

- listado;
- consulta individual.

### manage_academic_followups

Permite registrar y actualizar seguimientos académicos.

Aplica a operaciones de:

- creación;
- actualización parcial.

La pertenencia al grupo `DOCENTE` no sustituye la comprobación del permiso funcional.

Ambas condiciones deben cumplirse.

## 9. Alcance por asignación profesional

Los docentes únicamente pueden operar sobre estudiantes con una asignación profesional activa bajo:

```text
professional_role = DOCENTE
```

Una asignación existente en otro contexto no concede acceso académico.

Una asignación inactiva tampoco concede acceso.

La validación debe realizarse en Django antes de retornar o modificar información.

React no constituye una barrera de seguridad.

## 10. Registro académico

El registro de un seguimiento académico utiliza la entidad `AcademicFollowUp`.

El docente debe indicar:

- estudiante;
- fecha del seguimiento;
- período académico;
- asignatura;
- observaciones;
- fortalezas, cuando correspondan;
- áreas de mejora, cuando correspondan;
- recomendaciones, cuando correspondan.

El backend establece automáticamente:

- `created_by`;
- `updated_by`;
- `created_at`;
- `updated_at`.

No debe permitirse registrar un seguimiento para un estudiante:

- no asignado al docente;
- con asignación docente inactiva;
- inactivo institucionalmente;
- fuera del contexto `DOCENTE`.

## 11. Validaciones

### Fecha

`followup_date` no puede ser una fecha futura.

### Período académico

`academic_period` es obligatorio y no debe contener únicamente espacios en blanco.

Longitud máxima:

```text
50 caracteres
```

### Asignatura

`subject` es obligatorio y no debe contener únicamente espacios en blanco.

Longitud máxima:

```text
120 caracteres
```

### Observaciones

`observations` es obligatorio y no debe contener únicamente espacios en blanco.

### Estudiante

Una vez creado el seguimiento académico, el estudiante asociado no puede cambiarse mediante una actualización.

Esta restricción evita trasladar accidentalmente información histórica de un estudiante a otro.

## 12. Consulta académica

El dominio permite:

- listar seguimientos autorizados;
- consultar un seguimiento individual;
- filtrar seguimientos por estudiante.

La consulta debe respetar siempre:

- contexto `DOCENTE`;
- permiso `view_academic_followups`;
- asignación activa;
- alcance del docente autenticado;
- autoría del seguimiento.

Cada docente únicamente puede listar, consultar y actualizar seguimientos académicos creados por él mismo.

La existencia de una asignación activa con un estudiante no concede acceso a seguimientos creados por otro docente.

Esta restricción mantiene separados los registros académicos producidos por distintos profesionales, incluso cuando más de un docente tenga asignado al mismo estudiante.

## 13. Actualización académica

La actualización se realiza de forma parcial.

El docente autorizado puede actualizar los campos académicos editables del seguimiento.

La actualización solo puede realizarse sobre seguimientos creados por el propio docente autenticado.

No puede modificar la relación con el estudiante.

En cada actualización:

```text
updated_by = usuario autenticado
```

y `updated_at` debe reflejar automáticamente el momento de la modificación.

La creación original permanece identificada mediante `created_by` y `created_at`.

## 14. Política de eliminación

El seguimiento académico representa información histórica.

El flujo funcional actual no contempla eliminación física mediante la API.

No debe incorporarse una operación `DELETE` como parte de HU-11 sin una decisión arquitectónica explícita posterior.

La conservación histórica permite mantener trazabilidad sobre la atención académica brindada al estudiante.

## 15. API conceptual

El recurso académico se expone mediante:

```text
academic-followups
```

Operaciones previstas:

| Método | Operación |
| --- | --- |
| `GET` | Listar seguimientos académicos autorizados |
| `GET /{id}` | Consultar un seguimiento autorizado |
| `POST` | Registrar seguimiento |
| `PATCH /{id}` | Actualizar parcialmente un seguimiento |

No se contempla:

```text
DELETE
PUT
```

dentro del contrato actual.

## 16. Integración con el expediente

La sección académica forma parte del expediente integral del estudiante, pero mantiene su propio dominio y reglas de autorización.

El expediente no debe mezclar físicamente información académica, psicológica y terapéutica en una única tabla.

La información académica únicamente puede exponerse cuando el contexto y las reglas de acceso correspondientes lo permitan.

## 17. Frontend

La implementación frontend existente se organiza principalmente mediante:

```text
frontend/src/features/academic/
```

Actualmente incluye componentes y servicios para:

- formulario de seguimiento;
- listado de seguimientos;
- creación;
- actualización.

La funcionalidad también se integra en el expediente del estudiante.

El frontend debe:

- solicitar únicamente operaciones permitidas;
- presentar mensajes de validación;
- trabajar bajo el contexto `DOCENTE`;
- ocultar acciones no disponibles como mejora de experiencia de usuario.

Sin embargo, la autorización definitiva siempre corresponde al backend Django.

## 18. Seguridad

Las reglas de seguridad del seguimiento académico son:

- autenticación obligatoria;
- contexto `DOCENTE`;
- rol `DOCENTE`;
- permisos funcionales explícitos;
- asignación profesional activa;
- aislamiento entre contextos;
- validación en backend;
- protección de información histórica;
- trazabilidad de creación y modificación.

El rol `ADMINISTRADOR` no obtiene acceso académico automáticamente.

El rol `RESPONSABLE_INSTITUCIONAL` tampoco obtiene acceso al contenido académico únicamente por administrar estudiantes o asignaciones.

Los roles `PSICOLOGO` y `TERAPEUTA` no pueden acceder a esta información mediante sus contextos respectivos.

## 19. Responsabilidad por capas

### React

Responsable de:

- interfaz de usuario;
- formularios;
- presentación de información;
- consumo de API;
- validaciones de experiencia de usuario.

### Django REST Framework

Responsable de:

- autenticación;
- autorización;
- alcance por estudiante;
- validaciones;
- serialización;
- auditoría;
- reglas de negocio.

### SQL Server

Responsable de:

- persistencia relacional;
- restricciones derivadas del modelo;
- índices;
- integridad de referencias.

React nunca accede directamente a SQL Server.

## 20. Relación con las tareas de HU-11

### TASK-61 — Diseñar estructura del seguimiento académico

Formaliza mediante este documento la estructura académica existente y sus reglas.

No requiere crear una segunda implementación.

### TASK-62 — Crear estructura de base de datos académica

Deberá verificar la estructura existente de `AcademicFollowUp` y su migración.

Si la estructura satisface este diseño, la tarea se cerrará mediante validación y trazabilidad sin generar una tabla duplicada.

### TASK-63 — Implementar registro académico

Deberá verificar el flujo de creación existente.

Solo se modificarán componentes si se identifica un requerimiento de HU-11 que actualmente no esté cubierto.

### TASK-64 — Implementar consulta académica

Deberá verificar listado, consulta individual, filtros, permisos y alcance existentes.

No se creará un segundo endpoint para una funcionalidad ya cubierta.

### TASK-65 — Implementar actualización del seguimiento

Deberá validar la actualización parcial existente, sus restricciones y auditoría.

Solo se implementarán faltantes reales.

### TASK-66 — Probar seguimiento académico

Deberá auditar las pruebas existentes y completar únicamente escenarios de aceptación que todavía no cuenten con cobertura.

## 21. Decisión arquitectónica

HU-11 reutiliza la implementación académica creada previamente como parte de la construcción del expediente integral.

La decisión es:

> Mantener `AcademicFollowUp` como entidad canónica del seguimiento académico y evolucionar la implementación existente únicamente cuando HU-11 identifique faltantes verificables.

No se crearán estructuras paralelas, endpoints duplicados ni componentes frontend equivalentes para satisfacer artificialmente las tareas del backlog.

La finalización de cada tarea se demostrará mediante trazabilidad, validación técnica y, únicamente cuando corresponda, cambios incrementales sobre la implementación existente.
