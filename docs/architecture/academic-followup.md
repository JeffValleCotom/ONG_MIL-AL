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

## 22. Validación de TASK-62 — Estructura de base de datos académica

TASK-62 requiere crear la estructura de base de datos necesaria para almacenar el seguimiento académico.

Durante la ejecución de HU-11 se verificó que esta estructura ya había sido implementada previamente como dependencia de HU-07.

Por lo tanto, no se crea una segunda tabla ni una nueva migración equivalente.

### Modelo canónico

La estructura persistente continúa siendo:

`AcademicFollowUp`

definida en:

```text
backend/apps/academic/models.py
```

y materializada inicialmente mediante:

```text
backend/apps/academic/migrations/0001_initial.py
```

### Estado de la migración

La migración académica existente fue verificada mediante Django y se encuentra aplicada:

```text
academic
 [X] 0001_initial
```

La comparación entre el modelo actual y el estado de migraciones reportó:

```text
No changes detected in app 'academic'
```

Esto confirma que no existe actualmente una divergencia que requiera generar una migración adicional.

### Validación del proyecto Django

La comprobación general del proyecto reportó:

```text
System check identified no issues (0 silenced).
```

Por lo tanto, la aplicación académica se encuentra correctamente integrada con la configuración actual de Django.

### Existencia de la tabla física

Mediante la introspección de la conexión configurada hacia SQL Server se confirmó la existencia de:

```text
academic_academicfollowup
```

La consulta de introspección retornó:

```text
True
```

Esto confirma que la estructura no existe únicamente como modelo o migración pendiente, sino que está materializada en la base de datos configurada.

### Columnas verificadas

La tabla física contiene:

```text
id
followup_date
academic_period
subject
observations
strengths
areas_for_improvement
recommendations
created_at
updated_at
created_by_id
student_id
updated_by_id
```

Estas columnas corresponden con la estructura definida para `AcademicFollowUp`.

Los campos de texto opcionales a nivel funcional, como:

```text
strengths
areas_for_improvement
recommendations
```

utilizan `blank=True` en Django pero permanecen `NOT NULL` en SQL Server.

Esto es consistente con el diseño actual: su ausencia se representa mediante una cadena vacía y no mediante un valor SQL `NULL`.

### Clave primaria

Se verificó una clave primaria sobre:

```text
id
```

correspondiente al identificador interno de `AcademicFollowUp`.

### Relaciones e integridad referencial

La tabla contiene las relaciones esperadas:

```text
created_by_id -> users_user.id
student_id    -> students_student.id
updated_by_id -> users_user.id
```

Estas relaciones preservan la asociación con el estudiante y la trazabilidad de creación y actualización.

### Índice académico

Se verificó físicamente el índice:

```text
academic_student_date_idx
```

sobre:

```text
student_id
followup_date
```

El índice coincide con el definido en el modelo y facilita las consultas de seguimientos académicos por estudiante y fecha.

Además, SQL Server mantiene índices asociados a las claves foráneas de:

```text
created_by_id
student_id
updated_by_id
```

### Decisión de TASK-62

La estructura requerida por TASK-62 ya se encuentra implementada, migrada y materializada en SQL Server.

Por esta razón:

- no se modifica `AcademicFollowUp`;
- no se crea una tabla académica adicional;
- no se genera una migración `0002` sin una necesidad real;
- no se modifica la API ni el frontend;
- TASK-62 se completa mediante validación y trazabilidad de la implementación existente.

Cualquier cambio futuro en la estructura académica deberá responder a un requerimiento funcional verificable y producir su migración correspondiente mediante el flujo normal de Django.

Esta decisión evita duplicar una estructura que ya satisface el diseño definido por HU-11.

## 23. Validación de TASK-63 — Registro académico

TASK-63 requiere implementar el registro de seguimientos académicos para los estudiantes.

Durante la auditoría de HU-11 se confirmó que el flujo principal de registro académico ya había sido implementado previamente como parte de HU-07.

Por lo tanto, TASK-63 no introduce un segundo endpoint, un nuevo modelo, otro formulario ni un servicio frontend equivalente.

### Implementación existente reutilizada

El registro académico utiliza el modelo canónico:

`AcademicFollowUp`

y el endpoint existente:

```text
POST /api/v1/academic-followups/?context=DOCENTE
```

El servicio frontend correspondiente se encuentra en:

```text
frontend/src/features/academic/services/academicService.js
```

mediante:

```text
createAcademicFollowUp(...)
```

El formulario existente se encuentra en:

```text
frontend/src/features/academic/components/AcademicFollowUpForm.jsx
```

y está integrado en el expediente individual mediante:

```text
frontend/src/features/students/pages/StudentRecordPage.jsx
```

### Datos registrados

El formulario permite registrar:

```text
followup_date
academic_period
subject
observations
strengths
areas_for_improvement
recommendations
```

El identificador del estudiante se incorpora desde el expediente abierto y no es seleccionado libremente desde el formulario.

### Validaciones de entrada

El flujo existente exige `followup_date`, `academic_period`, `subject` y `observations`.

También impide fechas futuras, respeta las longitudes máximas definidas para período académico y materia, y normaliza los valores de texto antes del envío.

Las validaciones del frontend funcionan como apoyo de experiencia de usuario. Las reglas autoritativas de validación y seguridad permanecen en Django.

### Autorización del registro

El endpoint de creación requiere el contexto:

```text
DOCENTE
```

y el permiso funcional:

```text
manage_academic_followups
```

Además, se verifica que el usuario posea una asignación profesional activa con el estudiante bajo el rol `DOCENTE`.

Un docente no puede registrar seguimientos para estudiantes fuera de su alcance profesional activo.

### Estado del estudiante

No se permite registrar nuevos seguimientos académicos para estudiantes inactivos.

Esta regla se valida en backend y también se refleja en la interfaz mediante la disponibilidad de la acción de registro.

### Auditoría

Al crear un seguimiento académico, los campos:

```text
created_by
updated_by
```

se establecen a partir del usuario autenticado.

La autoría no se recibe desde el cliente.

### Faltante identificado durante TASK-63

La auditoría determinó que el backend académico ya protegía correctamente la creación mediante `manage_academic_followups`, pero el contrato del expediente no exponía una capability equivalente para el frontend.

Como consecuencia, la interfaz podía mostrar la acción `Registrar seguimiento` basándose únicamente en que el estudiante estuviera activo, aunque el usuario no tuviera permiso funcional para administrar seguimientos académicos.

La seguridad del endpoint no estaba comprometida, porque Django continuaba rechazando operaciones no autorizadas. Sin embargo, existía una inconsistencia entre la autorización del backend y las acciones presentadas por la interfaz.

### Capability académica

Para resolver el faltante sin duplicar lógica de autorización se incorporó al contrato del expediente:

```text
manage_academic
```

La capability es calculada exclusivamente por Django.

Su valor es verdadero únicamente cuando el contexto es `DOCENTE` y el usuario posee:

```text
manage_academic_followups
```

El frontend no calcula permisos a partir de grupos ni replica la matriz RBAC. Únicamente consume la capability proporcionada por el backend.

### Integración frontend

`StudentRecordPage.jsx` transforma la capability en:

```text
canManageAcademic
```

La acción de registrar seguimiento se presenta únicamente cuando `canManageAcademic` es verdadero, el estudiante se encuentra activo y no existe otro formulario académico abierto.

Esta condición controla únicamente la disponibilidad visual de la acción. El backend continúa siendo la autoridad final sobre el acceso.

### Cobertura agregada

Se verificó que un docente autorizado recibe:

```text
manage_academic = true
```

También se agregó cobertura para un docente que conserva:

```text
view_academic_followups
```

pero pierde:

```text
manage_academic_followups
```

En ese escenario, el expediente y la sección académica continúan disponibles, mientras que:

```text
manage_academic = false
```

Esta separación mantiene diferenciados los permisos de consulta y administración.

### Validación técnica

Se ejecutaron conjuntamente las pruebas del expediente estudiantil y del seguimiento académico:

```text
Found 39 test(s).
System check identified no issues (0 silenced).
Ran 39 tests.
OK
```

También se validó la compilación de producción del frontend mediante Vite:

```text
vite v8.3.4 building client environment for production...
66 modules transformed.
built successfully
```

### Alcance de TASK-63

TASK-63 reutiliza la implementación de registro académico existente y completa únicamente el contrato de autorización necesario para la interfaz.

No se modifica `AcademicFollowUp`, la estructura de base de datos, las migraciones, el serializer académico, el endpoint de creación, `createAcademicFollowUp` ni `AcademicFollowUpForm`.

La ampliación funcional realizada corresponde a `manage_academic` y a su consumo para controlar la disponibilidad visual de la acción de registro.

La actualización de seguimientos académicos y el control visual de las acciones de edición permanecen fuera del alcance de TASK-63 y serán auditados específicamente en TASK-65.

## 24. Validación de TASK-64 — Consulta académica

TASK-64 requiere implementar la consulta de seguimientos académicos registrados para los estudiantes.

Durante la auditoría de HU-11 se confirmó que esta funcionalidad ya había sido implementada previamente como parte de la integración académica del expediente estudiantil.

Por lo tanto, TASK-64 no introduce un nuevo endpoint, un servicio frontend duplicado ni un componente adicional para presentar información académica.

### Consulta académica existente

La API académica utiliza el ViewSet existente:

`AcademicFollowUpViewSet`

y permite operaciones de consulta mediante:

```text
GET /api/v1/academic-followups/?context=DOCENTE
GET /api/v1/academic-followups/{id}/?context=DOCENTE
```

Las acciones `list` y `retrieve` requieren el permiso funcional:

```text
view_academic_followups
```

La consulta académica también se integra en el expediente individual del estudiante mediante:

```text
GET /api/v1/students/{student_id}/record/?context=DOCENTE
```

El frontend obtiene este expediente mediante:

```text
getStudentRecord(...)
```

y presenta los seguimientos académicos existentes mediante:

```text
AcademicFollowUpList
```

### Información presentada

El historial académico muestra la información registrada en cada seguimiento, incluyendo:

```text
subject
academic_period
followup_date
observations
strengths
areas_for_improvement
recommendations
created_by
```

Cuando no existen seguimientos académicos disponibles, la interfaz presenta el estado vacío correspondiente.

### Alcance de consulta por docente

La consulta académica aplica restricciones tanto por asignación profesional como por autoría.

El queryset académico requiere que el estudiante posea una asignación profesional:

```text
professional = usuario autenticado
professional_role = DOCENTE
is_active = true
```

Además, los seguimientos se restringen mediante:

```text
created_by = usuario autenticado
```

Por lo tanto, una asignación activa con un estudiante no concede acceso automático a seguimientos creados por otro docente.

Cada docente consulta únicamente los seguimientos académicos creados por él mismo dentro de su alcance profesional activo.

### Filtro por estudiante

El listado permite filtrar mediante:

```text
student=<student_id>
```

El identificador recibido es validado antes de aplicar el filtro.

Debe ser un número entero mayor que cero.

Cuando el valor es válido, el queryset agrega la restricción:

```text
student_id = <student_id>
```

Este filtro no elimina las restricciones de autoría, contexto, permiso ni asignación profesional.

### Consulta individual

La consulta individual de un seguimiento utiliza el mismo queryset restringido que el listado.

Como consecuencia, un seguimiento fuera del alcance del docente no es recuperable directamente mediante su identificador.

La API responde como recurso no encontrado cuando el seguimiento no pertenece al queryset autorizado del usuario.

### Aislamiento entre docentes

Se encuentra cubierta específicamente la situación donde dos docentes tienen asignación activa sobre el mismo estudiante.

En ese escenario:

```text
Docente A -> seguimiento creado por Docente A
Docente B -> seguimiento creado por Docente B
```

cuando el Docente A consulta el historial del estudiante:

- recibe su propio seguimiento;
- no recibe el seguimiento creado por el Docente B;
- no puede consultar directamente el seguimiento del Docente B.

Esto confirma que la asignación compartida de un estudiante no produce intercambio de información académica entre docentes.

### Aislamiento por contexto

La API académica exige explícitamente:

```text
context=DOCENTE
```

La ausencia del contexto es rechazada.

Un usuario con múltiples roles no puede utilizar su pertenencia al grupo `DOCENTE` para acceder a la información académica mientras opera bajo otro contexto profesional.

Por ejemplo, el contexto:

```text
PSICOLOGO
```

no habilita el acceso a la API académica aunque el mismo usuario también posea el rol `DOCENTE`.

El rol `RESPONSABLE_INSTITUCIONAL` tampoco obtiene acceso a la API de seguimientos académicos mediante el contexto `DOCENTE`.

### Integración con el expediente

En contexto `DOCENTE`, el expediente individual incluye una sección:

```text
academic
```

cuando el usuario posee el permiso correspondiente.

Esta sección contiene los seguimientos académicos autorizados para el docente y es consumida por `StudentRecordPage.jsx`.

La interfaz delega la presentación del historial en:

```text
AcademicFollowUpList.jsx
```

No se realiza acceso directo desde React a SQL Server ni se replica en frontend la lógica de autorización.

### Seguridad de la consulta

Django continúa siendo la autoridad de seguridad.

La visibilidad frontend no sustituye las validaciones de backend.

La consulta requiere conjuntamente:

```text
usuario autenticado
contexto DOCENTE
rol DOCENTE
view_academic_followups
asignación profesional DOCENTE activa
autoría del seguimiento
```

El filtro opcional por estudiante únicamente reduce el queryset que ya fue autorizado y no amplía su alcance.

### Cobertura existente

Las pruebas existentes verifican, entre otros escenarios:

```text
docente asignado puede listar seguimientos
docente solo lista estudiantes dentro de su alcance
docente no puede recuperar un seguimiento no autorizado
contexto obligatorio
aislamiento multirrol por contexto
responsable institucional sin acceso académico
aislamiento entre docentes asignados al mismo estudiante
filtro de listado por estudiante
consulta individual fuera del alcance retorna 404
```

La cobertura específica de dos docentes asignados al mismo estudiante confirma tanto el filtrado por autor como el comportamiento de `?student=`.

### Validación técnica

Durante la auditoría de TASK-64 se ejecutaron conjuntamente las pruebas académicas y las pruebas del expediente:

```text
Found 39 test(s).
System check identified no issues (0 silenced).
Ran 39 tests.
OK
```

Esto confirma que la consulta académica y su integración con el expediente continúan funcionando sobre la versión actual de HU-11.

### Decisión de TASK-64

La funcionalidad requerida por TASK-64 ya se encuentra implementada y cubierta por las pruebas existentes.

Por esta razón:

- no se crea un nuevo endpoint de consulta;
- no se crea un servicio frontend académico equivalente;
- no se modifica `AcademicFollowUpViewSet`;
- no se modifica `AcademicFollowUpList`;
- no se agregan pruebas redundantes en esta tarea;
- TASK-64 se completa mediante auditoría, validación y trazabilidad.

Las pruebas finales de aceptación correspondientes al seguimiento académico serán revisadas de forma integral en TASK-66.

## 25. Validación de TASK-65 — Actualización del seguimiento

TASK-65 requiere implementar la actualización de los seguimientos académicos registrados.

Durante la auditoría de HU-11 se confirmó que el flujo principal de actualización ya había sido implementado previamente junto con la integración académica del expediente.

Por lo tanto, TASK-65 no introduce un segundo endpoint de actualización, otro formulario ni un servicio frontend equivalente.

### Implementación existente reutilizada

La API académica utiliza el endpoint existente:

```text
PATCH /api/v1/academic-followups/{id}/?context=DOCENTE
```

La acción `partial_update` requiere el permiso funcional:

```text
manage_academic_followups
```

El frontend utiliza el servicio existente:

```text
updateAcademicFollowUp(...)
```

que realiza la solicitud mediante `PATCH`.

El formulario `AcademicFollowUpForm` también se reutiliza para la edición mediante `initialFollowUp`.

Cuando existe un seguimiento en edición, el formulario carga los valores actuales y presenta la acción:

```text
Guardar cambios
```

### Flujo frontend de actualización

`StudentRecordPage.jsx` conserva en estado el seguimiento seleccionado para edición.

Cuando el formulario se envía y existe `editingFollowUp`, se ejecuta:

```text
updateAcademicFollowUp(...)
```

utilizando:

```text
followUpId
context
followUpData
```

Después de una actualización exitosa:

- se cierra el formulario;
- se limpia el seguimiento en edición;
- se presenta un mensaje de confirmación;
- se vuelve a consultar el expediente para actualizar la información mostrada.

No se implementa un flujo paralelo de actualización.

### Campos actualizables

La actualización reutiliza los campos del seguimiento académico:

```text
followup_date
academic_period
subject
observations
strengths
areas_for_improvement
recommendations
```

Las validaciones existentes del serializer y del formulario continúan aplicándose durante la edición.

### Inmutabilidad del estudiante

El estudiante asociado a un seguimiento académico no puede modificarse durante una actualización.

Si una solicitud `PATCH` contiene:

```text
student_id
```

la API rechaza la operación.

Esta regla evita trasladar un seguimiento histórico de un estudiante hacia otro.

### Auditoría de actualización

El campo:

```text
updated_by
```

es establecido por Django a partir del usuario autenticado que realiza la actualización.

El cliente no controla el valor de auditoría.

El campo `created_by` conserva al autor original del seguimiento.

### Alcance de autorización

La actualización utiliza el mismo queryset restringido aplicado a la consulta académica.

Por lo tanto, el usuario solo puede actualizar seguimientos que:

```text
fueron creados por el propio usuario
pertenecen a un estudiante dentro de su asignación DOCENTE activa
```

Además, la operación requiere:

```text
context=DOCENTE
manage_academic_followups
```

El permiso de consulta:

```text
view_academic_followups
```

no concede por sí solo capacidad de actualización.

### Faltante identificado durante TASK-65

La API ya diferenciaba correctamente los permisos de consulta y administración.

Sin embargo, la interfaz enviaba siempre:

```text
onEdit={handleAcademicEdit}
```

a `AcademicFollowUpList`.

El componente muestra la acción `Editar` siempre que recibe `onEdit`.

Como consecuencia, un docente con acceso de consulta pero sin `manage_academic_followups` podía visualizar una acción de edición que posteriormente sería rechazada correctamente por Django.

La seguridad backend no estaba comprometida, pero existía una inconsistencia entre las acciones visibles en frontend y las capacidades autorizadas por el servidor.

### Corrección frontend

TASK-65 reutiliza la capability incorporada previamente:

```text
manage_academic
```

`StudentRecordPage.jsx` ahora proporciona `handleAcademicEdit` únicamente cuando:

```text
canManageAcademic = true
```

Cuando la capability es falsa, `AcademicFollowUpList` recibe `onEdit` como `undefined`.

El componente ya estaba preparado para este comportamiento y no requiere modificaciones adicionales, porque solo renderiza el botón `Editar` cuando existe un callback de edición.

De esta forma, la interfaz consume la autorización calculada por Django sin replicar grupos, permisos ni reglas RBAC en React.

### Separación entre consulta y actualización

Se agregó una prueba específica para un docente que conserva acceso de consulta pero pierde:

```text
manage_academic_followups
```

En ese escenario se verifica que:

```text
GET detalle -> 200 OK
PATCH detalle -> 403 Forbidden
```

También se comprueba que el contenido original del seguimiento permanece sin modificaciones después del intento rechazado.

Esta cobertura demuestra explícitamente que:

```text
view_academic_followups != manage_academic_followups
```

y que consultar un seguimiento no implica autorización para actualizarlo.

### Cobertura existente conservada

Las pruebas existentes continúan verificando:

```text
docente autorizado puede actualizar su seguimiento
updated_by registra al usuario autenticado
student_id no puede modificarse
otro docente no puede actualizar el seguimiento
DELETE continúa deshabilitado
```

TASK-65 agrega únicamente la cobertura faltante sobre separación entre permisos de consulta y actualización.

### Validación técnica

Después de los cambios se ejecutaron conjuntamente las pruebas académicas y del expediente:

```text
Found 40 test(s).
System check identified no issues (0 silenced).
Ran 40 tests.
OK
```

También se validó la compilación de producción del frontend:

```text
vite v8.3.4 building client environment for production...
66 modules transformed.
built successfully
```

`git diff --check` no reportó errores de formato.

### Decisión de TASK-65

TASK-65 reutiliza el mecanismo existente de actualización y corrige únicamente el faltante real encontrado durante la auditoría.

No se modifican:

```text
AcademicFollowUp
estructura de base de datos
migraciones
AcademicFollowUpSerializer
AcademicFollowUpViewSet
academicService.js
AcademicFollowUpForm.jsx
AcademicFollowUpList.jsx
```

Los cambios funcionales se limitan a:

```text
controlar la disponibilidad visual de Editar mediante manage_academic
agregar cobertura de autorización view frente a manage
```

Django continúa siendo la autoridad final de seguridad aunque la interfaz oculte las acciones no autorizadas.
