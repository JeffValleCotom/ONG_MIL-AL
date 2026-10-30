# Diseño del expediente individual del estudiante

## HU-07 - Expediente individual del estudiante

## 1. Objetivo

Definir la arquitectura del expediente individual de los estudiantes de
MIL-AL, considerando:

- separación entre información general, académica, psicológica y terapéutica;
- acceso únicamente a estudiantes asignados;
- separación de los espacios de trabajo de cada profesional;
- autorización en backend;
- mínimo privilegio;
- trazabilidad de asignaciones;
- integración entre React, Django y SQL Server.

El expediente se construirá sobre la entidad `Student` implementada en
HU-06, sin duplicar su información general.

## 2. Principios de diseño

La implementación de HU-07 seguirá los siguientes principios:

- `Student` continúa siendo la entidad raíz del estudiante;
- el expediente no se almacenará como una tabla con todos los datos mezclados;
- la información académica, psicológica y terapéutica utilizará estructuras
  independientes;
- un permiso funcional no concede acceso automático a todos los estudiantes;
- los profesionales solo podrán consultar estudiantes que tengan asignados;
- el alcance por estudiante se validará siempre en Django;
- React únicamente reflejará las acciones autorizadas;
- los distintos profesionales tendrán espacios de trabajo separados;
- no se realizará eliminación física de asignaciones o información histórica;
- el rol `ADMINISTRADOR` no concede acceso automático al expediente;
- el rol `RESPONSABLE_INSTITUCIONAL` no concede acceso automático a
  información psicológica o terapéutica sensible.

## 3. Expediente como agregado lógico

El expediente individual se define conceptualmente como:

Student
|
|-- información general
|-- asignaciones profesionales
|-- información académica
|-- información psicológica
|-- información terapéutica / intervenciones
|-- evaluaciones estructuradas
|-- metadatos y trazabilidad

No se creará inicialmente una tabla `StudentRecord` únicamente para representar
la existencia del expediente.

El expediente será un recurso lógico construido a partir de `Student` y de sus
entidades relacionadas.

Solo se creará una entidad física adicional para el expediente si posteriormente
se identifican metadatos propios que no pertenezcan a ninguna de sus secciones.

## 4. Asignación profesional - estudiante

Para garantizar que cada profesional consulte únicamente a sus estudiantes se
requiere una relación explícita entre usuarios institucionales y estudiantes.

Entidad conceptual:

`StudentProfessionalAssignment`

Campos propuestos:

| Campo | Descripción |
| --- | --- |
| `id` | Identificador interno |
| `student` | Estudiante asignado |
| `professional` | Usuario institucional asignado |
| `professional_role` | Rol bajo el cual atiende al estudiante |
| `is_active` | Estado de la asignación |
| `assigned_at` | Fecha y hora de asignación |
| `unassigned_at` | Fecha y hora de finalización |
| `assigned_by` | Usuario institucional que realizó la asignación |
| `created_at` | Fecha de creación |
| `updated_at` | Fecha de última modificación |

Los valores permitidos para `professional_role` serán:

- `DOCENTE`;
- `PSICOLOGO`;
- `TERAPEUTA`.

`RESPONSABLE_INSTITUCIONAL` gestionará las asignaciones, pero no será tratado
como profesional asignado dentro de esta relación.

`ADMINISTRADOR` tampoco será un profesional asignable.

## 5. Razón de professional_role

La relación no dependerá únicamente de los grupos actuales del usuario.

Un usuario puede pertenecer técnicamente a varios roles institucionales.

Ejemplo:

Usuario:
- DOCENTE;
- PSICOLOGO.

Asignación:
- estudiante A;
- usuario;
- `professional_role = DOCENTE`.

Esta asignación autoriza al usuario a trabajar con el estudiante A únicamente
dentro de su contexto docente.

No autoriza por sí sola el acceso a la sección psicológica del mismo estudiante.

Para acceder como psicólogo deberá existir una asignación activa independiente
con:

`professional_role = PSICOLOGO`.

## 6. Reglas de una asignación

Al crear una asignación deberán cumplirse como mínimo las siguientes reglas:

- el estudiante debe existir;
- el profesional debe existir;
- el profesional debe estar activo;
- el rol indicado debe ser un rol profesional válido;
- el usuario debe poseer actualmente el rol indicado;
- no debe existir otra asignación activa equivalente;
- `assigned_by` debe ser un usuario autorizado para gestionar asignaciones.

Una asignación inactiva no concede acceso.

La eliminación física no estará permitida.

Al finalizar una asignación se establecerán:

- `is_active = false`;
- `unassigned_at`.

La implementación deberá impedir asignaciones activas duplicadas para la misma
combinación:

- estudiante;
- profesional;
- rol profesional.

La estrategia concreta de restricción compatible con SQL Server será validada
durante la implementación mediante migraciones Django.

## 7. Cálculo del acceso efectivo

El acceso efectivo no dependerá únicamente del permiso Django.

Para un profesional deberán cumplirse simultáneamente:

1. usuario autenticado;
2. usuario activo;
3. rol profesional correcto;
4. permiso funcional requerido;
5. asignación activa con el estudiante;
6. asignación realizada bajo el contexto profesional correspondiente.

Conceptualmente:

permiso funcional
+
rol profesional
+
asignación activa
+
sección autorizada
=
acceso efectivo

Si cualquiera de las condiciones falla, Django deberá rechazar el acceso.

## 8. Alcance de estudiantes

### DOCENTE

Solo podrá obtener estudiantes que tengan una asignación activa:

`professional_role = DOCENTE`

para `request.user`.

### PSICOLOGO

Solo podrá obtener estudiantes que tengan una asignación activa:

`professional_role = PSICOLOGO`

para `request.user`.

### TERAPEUTA

Solo podrá obtener estudiantes que tengan una asignación activa:

`professional_role = TERAPEUTA`

para `request.user`.

### RESPONSABLE_INSTITUCIONAL

Mantendrá la capacidad institucional para gestionar información general de
estudiantes y administrar asignaciones.

Su acceso institucional no implica autorización para consultar contenido
psicológico o terapéutico sensible.

### ADMINISTRADOR

Continuará limitado a las funciones administrativas definidas por sus permisos.

No obtendrá acceso a estudiantes ni expedientes únicamente por poseer el rol
`ADMINISTRADOR`.

## 9. Estudiantes inactivos

La desactivación de un estudiante no elimina su información ni sus relaciones.

Un estudiante inactivo podrá conservar asignaciones e historial para efectos de
consulta autorizada.

Las funcionalidades que creen nuevos seguimientos deberán decidir explícitamente
si admiten operaciones sobre estudiantes inactivos.

Como regla inicial, no se deberán crear nuevas atenciones operativas para un
estudiante inactivo.

## 10. Separación de secciones del expediente

### Información general

Origen:

`Student`

Contenido:

- código institucional;
- nombres;
- apellidos;
- fecha de nacimiento;
- fecha de ingreso;
- estado.

Los profesionales solo podrán consultar estos datos cuando exista una asignación
válida con el estudiante.

### Información académica

Será accesible dentro del contexto `DOCENTE`.

Requerirá:

- rol `DOCENTE`;
- asignación activa como `DOCENTE`;
- `view_academic_followups` para consulta;
- `manage_academic_followups` para registro o modificación.

### Información psicológica

Será accesible dentro del contexto `PSICOLOGO`.

Requerirá:

- rol `PSICOLOGO`;
- asignación activa como `PSICOLOGO`;
- `view_psychological_followups` para consulta;
- `manage_psychological_followups` para registro o modificación.

### Información terapéutica

Será accesible dentro del contexto `TERAPEUTA`.

Requerirá:

- rol `TERAPEUTA`;
- asignación activa como `TERAPEUTA`;
- `view_therapy_followups` para consulta;
- `manage_therapy_followups` para registro o modificación.

La información terapéutica se mantiene separada de las notas psicológicas.

Para las acciones de registro y actualización, el expediente expone la capability:

`manage_therapy`

Esta capability es calculada por Django y es verdadera únicamente cuando el contexto es `TERAPEUTA` y el usuario posee `manage_therapy_followups`.

El frontend utiliza esta capability para controlar la disponibilidad visual de las acciones de registrar y editar seguimientos terapéuticos. Django continúa siendo la autoridad final de autorización.

### Evaluaciones

Las evaluaciones estructuradas podrán ser utilizadas dentro de los contextos
profesionales:

- `DOCENTE`;
- `PSICOLOGO`;
- `TERAPEUTA`.

Para consultar evaluaciones deberán cumplirse simultáneamente:

- rol correspondiente al contexto profesional solicitado;
- asignación activa con el estudiante bajo ese mismo contexto;
- permiso `view_evaluations`.

Para registrar o actualizar evaluaciones se requerirá adicionalmente:

- permiso `manage_evaluations`.

Cada evaluación conserva el contexto profesional en `professional_role`, además
de los usuarios responsables de creación y última actualización.

Las evaluaciones permanecen aisladas entre contextos profesionales. Una
evaluación registrada en contexto `PSICOLOGO`, por ejemplo, no será expuesta
desde el contexto `TERAPEUTA` o `DOCENTE`.

Dentro de un mismo contexto profesional, un profesional actualmente asignado al
estudiante podrá consultar evaluaciones históricas registradas previamente por
otro profesional del mismo contexto. Esto permite conservar continuidad del
seguimiento sin perder la trazabilidad del autor original.

Para las acciones de registro y actualización, el expediente expone la
capability:

`manage_evaluations`

Esta capability es calculada por Django según el contexto profesional actual y
el permiso `manage_evaluations`. React la utiliza únicamente para controlar la
disponibilidad visual de las acciones; Django continúa siendo la autoridad final
de autorización.

## 11. Matriz de visibilidad del expediente

| Información | Administrador | Docente asignado | Psicólogo asignado | Terapeuta asignado | Responsable institucional |
| --- | :---: | :---: | :---: | :---: | :---: |
| Datos generales | No | Sí | Sí | Sí | Sí |
| Información académica | No | Sí | No | No | No |
| Información psicológica | No | No | Sí | No | No |
| Información terapéutica | No | No | No | Sí | No |
| Evaluaciones del contexto profesional | No | Sí | Sí | Sí | No |
| Gestión de asignaciones | No | No | No | No | Sí |

La columna "asignado" implica que debe existir una asignación activa bajo el rol
correspondiente.

## 12. Permiso para administrar asignaciones

Se requiere un permiso funcional adicional:

`manage_student_assignments`

Responsabilidad:

- consultar asignaciones institucionales;
- asignar profesionales;
- finalizar asignaciones;
- consultar el historial necesario para gestión institucional.

Inicialmente será concedido únicamente a:

`RESPONSABLE_INSTITUCIONAL`.

No será concedido automáticamente a:

- `ADMINISTRADOR`;
- `DOCENTE`;
- `PSICOLOGO`;
- `TERAPEUTA`.

## 13. Cambios sobre la consulta general de estudiantes

HU-06 permitió a los roles profesionales utilizar `view_students`.

HU-07 agrega una restricción adicional.

Después de implementar las asignaciones:

- `RESPONSABLE_INSTITUCIONAL` podrá consultar los estudiantes de alcance
  institucional;
- `DOCENTE` solo recibirá estudiantes asignados como docente;
- `PSICOLOGO` solo recibirá estudiantes asignados como psicólogo;
- `TERAPEUTA` solo recibirá estudiantes asignados como terapeuta.

La misma restricción deberá aplicarse tanto al listado como a la consulta por ID.

Conocer el identificador de un estudiante no deberá permitir eludir la
restricción de asignación.

## 14. Defensa contra acceso directo

Las restricciones no dependerán de que React oculte enlaces.

Ejemplo no permitido:

un docente conoce manualmente:

`/api/v1/students/50/`

pero no está asignado al estudiante 50.

Resultado esperado:

- Django no deberá retornar la información del estudiante.

Esta regla deberá verificarse mediante pruebas automatizadas.

## 15. Espacios de trabajo separados en frontend

La implementación actual utiliza `StudentManagementPage` para varios roles.

HU-07 reemplazará ese comportamiento profesional por espacios separados.

Arquitectura conceptual:

`ADMINISTRADOR`
→ inicio administrativo

`RESPONSABLE_INSTITUCIONAL`
→ inicio institucional

`DOCENTE`
→ inicio docente

`PSICOLOGO`
→ inicio de psicología

`TERAPEUTA`
→ inicio de terapia

Cada inicio tendrá su propio componente de página.

Los componentes visuales reutilizables podrán compartirse, pero las páginas de
inicio y sus flujos funcionales permanecerán separados.

## 16. Organización frontend prevista

Estructura conceptual:

frontend/src/features/
- academic/
  - pages/TeacherHomePage.jsx
- psychology/
  - pages/PsychologistHomePage.jsx
- therapy/
  - pages/TherapistHomePage.jsx
- institutional/
  - pages/InstitutionalHomePage.jsx
- students/
  - componentes reutilizables
- users/
  - administración de usuarios

`StudentManagementPage` quedará asociado al contexto institucional y dejará de
ser la pantalla de inicio compartida por todos los profesionales.

## 17. Usuarios con múltiples roles

La plataforma permite que un usuario pertenezca técnicamente a más de un grupo.

Si un usuario posee varios contextos funcionales, estos no deberán fusionarse en
un único dashboard.

El frontend deberá permitir ingresar al espacio correspondiente al contexto
autorizado.

Ejemplo:

usuario:
- DOCENTE;
- PSICOLOGO.

El sistema podrá ofrecer:

- Inicio docente;
- Inicio de psicología.

Cada espacio deberá aplicar sus permisos y asignaciones de forma independiente.

## 18. Backend por contexto profesional

La unión de permisos de los grupos de un usuario no será suficiente para decidir
qué registros puede consultar.

Las consultas de información sensible deberán comprobar el contexto profesional
correspondiente.

Ejemplo:

un usuario posee:

- rol DOCENTE;
- rol PSICOLOGO;
- asignación DOCENTE con estudiante A;
- asignación PSICOLOGO con estudiante B.

Resultado:

- desde el contexto académico puede trabajar con A;
- desde el contexto psicológico puede trabajar con B;
- la asignación docente con A no habilita información psicológica de A;
- la asignación psicológica con B no habilita información académica de B.

## 19. Contrato conceptual del expediente

El recurso de expediente deberá poder representar únicamente la información que
el usuario esté autorizado a consultar.

Conceptualmente:

GET `/api/v1/students/{id}/record/`

La respuesta no deberá construir un expediente completo y posteriormente ocultar
campos en React.

Django deberá excluir o rechazar las secciones no autorizadas antes de enviar la
respuesta.

TASK-38 definirá el contrato inicial del endpoint.

TASK-39 incorporará la información académica.

TASK-40 incorporará la información psicológica y terapéutica.

TASK-41 implementará la consulta integral respetando las reglas de visibilidad.

## 20. Gestión de asignaciones

La administración de asignaciones requerirá funcionalidad backend y frontend.

Backend:

- crear asignación;
- consultar asignaciones;
- finalizar asignación;
- validar rol profesional;
- validar usuario activo;
- impedir duplicados activos;
- aplicar `manage_student_assignments`;
- filtrar estudiantes por asignación.

Frontend institucional:

- seleccionar estudiante;
- seleccionar profesional;
- seleccionar rol profesional válido;
- consultar asignaciones actuales;
- finalizar asignaciones;
- visualizar estados y errores de validación.

React no podrá decidir por sí mismo si una asignación es válida.

## 21. Tareas técnicas necesarias

TASK-37 define la arquitectura.

Antes de implementar el expediente completo se requiere incorporar una tarea
técnica para:

`Implementar asignación de profesionales a estudiantes`

Esta tarea deberá realizar backend y frontend de forma coordinada.

También se requiere separar los espacios de inicio profesionales antes de
exponer información del expediente.

La separación podrá implementarse dentro de una tarea técnica específica o
integrarse en la primera tarea de implementación de HU-07, siempre que se
mantenga trazabilidad en Azure DevOps.

## 22. Relación con las tareas de HU-07

### TASK-37 - Diseñar estructura del expediente

Define:

- estructura lógica;
- asignaciones;
- segregación de información;
- reglas de acceso;
- arquitectura frontend.

### TASK-38 - Implementar expediente individual

Implementará el recurso base del expediente y su contrato inicial.

### TASK-39 - Integrar información académica

Incorporará el dominio académico y las reglas del contexto DOCENTE.

### TASK-40 - Integrar información psicológica y terapéutica

Incorporará ambos dominios manteniendo aislamiento de información sensible.

### TASK-41 - Implementar consulta integral

Compondrá las secciones autorizadas del expediente sin violar las reglas de
alcance.

### TASK-42 - Probar expediente individual

Validará:

- permisos;
- asignaciones;
- aislamiento entre profesionales;
- acceso directo no autorizado;
- integración frontend/backend;
- persistencia;
- regresión general.

## 23. Criterios de seguridad obligatorios

HU-07 no se considerará completa si cualquiera de estos escenarios es posible:

- un profesional consulta un estudiante no asignado;
- un docente consulta información psicológica;
- un psicólogo consulta información académica sin autorización;
- un terapeuta consulta notas psicológicas;
- un responsable institucional consulta información sensible solo por gestionar
  estudiantes;
- un administrador obtiene acceso funcional por su rol administrativo;
- cambiar una URL permite eludir una asignación;
- React recibe información sensible para luego ocultarla visualmente.

La autorización y el alcance deberán resolverse antes de serializar la
información enviada al frontend.