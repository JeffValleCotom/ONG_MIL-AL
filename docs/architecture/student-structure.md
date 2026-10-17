# Diseño de la estructura de estudiantes

## HU-06 - Registro y gestión de estudiantes

La plataforma MIL-AL permitirá registrar, consultar, actualizar,
activar y desactivar estudiantes atendidos por la institución.

La entidad Student contendrá únicamente información general de
identificación y administración del estudiante.

La información académica, psicológica, terapéutica, familiar y
documental se gestionará mediante entidades independientes en las
historias de usuario correspondientes.

## 1. Objetivo

Definir la estructura base del estudiante y el contrato que utilizarán
el backend Django, la API REST y el frontend React durante HU-06.

El diseño debe permitir:

- registrar estudiantes;
- consultar estudiantes;
- actualizar información general;
- activar y desactivar estudiantes;
- restringir operaciones según permisos institucionales;
- utilizar al estudiante como entidad principal para las funcionalidades
  posteriores del expediente.

## 2. Arquitectura

La funcionalidad seguirá la arquitectura general de MIL-AL:

React
→ API REST
→ Django
→ SQL Server

React no accederá directamente a SQL Server.

La aplicación Django correspondiente se ubicará en:

backend/apps/students/

El modelo principal será:

Student

La creación de la aplicación, modelo y migración se realizará en
TASK-32.

## 3. Alcance de Student

Student representa la identidad institucional básica de un estudiante.

La tabla no debe almacenar directamente:

- seguimientos académicos;
- información psicológica;
- diagnósticos;
- información terapéutica;
- intervenciones;
- información familiar;
- responsables familiares;
- documentos o archivos;
- contraseñas;
- usuarios institucionales;
- contenido generado mediante inteligencia artificial.

Estas funcionalidades tendrán estructuras relacionadas con Student
en historias de usuario posteriores.

## 4. Estructura propuesta

| Campo | Tipo conceptual | Requerido | Editable | Descripción |
|---|---|:---:|:---:|---|
| id | entero/autogenerado | Sí | No | Identificador interno del estudiante |
| institutional_code | texto, máximo 30 | Sí | Sí | Código institucional único del estudiante |
| first_name | texto, máximo 100 | Sí | Sí | Nombres del estudiante |
| last_name | texto, máximo 100 | Sí | Sí | Apellidos del estudiante |
| date_of_birth | fecha | Sí | Sí | Fecha de nacimiento |
| admission_date | fecha | Sí | Sí | Fecha de ingreso a MIL-AL |
| is_active | booleano | Sí | Mediante acciones de estado | Indica si el estudiante se encuentra activo |
| created_at | fecha y hora | Automático | No | Fecha de creación del registro |
| updated_at | fecha y hora | Automático | No | Fecha de última actualización |

## 5. Identificación del estudiante

### id

Será la clave primaria interna de la base de datos.

No debe ser ingresada ni modificada por React.

Se utilizará para relacionar al estudiante con las entidades que se
implementen posteriormente.

Ejemplos:

- expediente;
- información familiar;
- documentos;
- seguimientos;
- intervenciones.

### institutional_code

Será el identificador institucional visible del estudiante.

Reglas:

- obligatorio;
- único;
- máximo 30 caracteres;
- se eliminarán espacios innecesarios al inicio y al final;
- se normalizará a mayúsculas;
- no se permitirá registrar dos estudiantes con el mismo código.

La unicidad debe garantizarse tanto mediante validación de aplicación
como mediante restricción en la base de datos.

## 6. Datos personales básicos

Los campos:

- first_name;
- last_name;

serán obligatorios.

Los valores deberán eliminar espacios innecesarios al inicio y final.

No se almacenará un campo full_name en la base de datos porque puede
obtenerse a partir de first_name y last_name.

Tampoco se almacenará la edad debido a que puede calcularse a partir
de date_of_birth y cambiaría con el tiempo.

## 7. Fechas

### date_of_birth

Será obligatoria.

No podrá contener una fecha futura.

### admission_date

Representará la fecha en la que el estudiante ingresó a la institución.

Será obligatoria y no podrá contener una fecha futura.

Tampoco podrá ser anterior a date_of_birth.

La fecha de ingreso es diferente de created_at:

- admission_date representa un dato institucional;
- created_at representa cuándo se creó el registro en el sistema.

## 8. Estado del estudiante

El campo is_active indicará el estado operativo del estudiante.

Valor inicial:

true

No se realizará eliminación física de estudiantes desde la aplicación.

Las operaciones de estado serán:

- activar;
- desactivar.

Esto permite conservar relaciones, historial y trazabilidad.

Un estudiante inactivo continuará existiendo en la base de datos y
podrá ser consultado por usuarios autorizados.

## 9. Información excluida de HU-06

La siguiente información no formará parte directamente de Student.

### Expediente

Se implementará en HU-07 y HU-08.

### Información familiar

Se implementará en HU-09 mediante entidades relacionadas con Student.

### Documentos

Se implementarán en HU-10.

### Información académica

Los datos de seguimiento académico pertenecerán a las funcionalidades
académicas correspondientes y se relacionarán con Student.

### Información psicológica y terapéutica

No se almacenará directamente en Student.

Por tratarse de información sensible, utilizará estructuras separadas
y permisos específicos.

## 10. Permisos

Se reutilizarán los permisos funcionales existentes:

### view_students

Permite:

- consultar el listado de estudiantes;
- consultar información general de un estudiante.

Actualmente corresponde a:

- DOCENTE;
- PSICOLOGO;
- TERAPEUTA;
- RESPONSABLE_INSTITUCIONAL.

### manage_students

Permite:

- registrar estudiantes;
- actualizar información general;
- activar estudiantes;
- desactivar estudiantes.

Actualmente corresponde a:

- RESPONSABLE_INSTITUCIONAL.

El rol ADMINISTRADOR no obtiene acceso automático a estudiantes.

La autorización se comprobará siempre en Django.

Ocultar botones en React será únicamente una medida de experiencia
de usuario y no un mecanismo de seguridad.

## 11. Endpoints previstos

### GET /api/v1/students/

Permiso requerido:

view_students

Responsabilidad:

- obtener estudiantes;
- permitir posteriormente búsqueda por código o nombre;
- permitir filtrar por estado.

### POST /api/v1/students/

Permiso requerido:

manage_students

Responsabilidad:

- registrar un estudiante;
- validar campos obligatorios;
- validar código institucional único;
- validar fechas;
- crear al estudiante inicialmente activo.

### GET /api/v1/students/{id}/

Permiso requerido:

view_students

Responsabilidad:

- consultar información general de un estudiante.

### PATCH /api/v1/students/{id}/

Permiso requerido:

manage_students

Responsabilidad:

- actualizar únicamente campos generales permitidos;
- impedir modificación directa de id, created_at y updated_at;
- manejar el estado mediante acciones específicas.

### PATCH /api/v1/students/{id}/activate/

Permiso requerido:

manage_students

Responsabilidad:

- establecer is_active en true.

### PATCH /api/v1/students/{id}/deactivate/

Permiso requerido:

manage_students

Responsabilidad:

- establecer is_active en false.

No se expondrá una operación DELETE para estudiantes.

## 12. Consulta y búsqueda

TASK-34 implementará la consulta de estudiantes.

El listado deberá contemplar búsqueda por:

- institutional_code;
- first_name;
- last_name.

También deberá poder filtrarse según:

- activos;
- inactivos.

La búsqueda no sustituirá los controles de autorización del backend.

## 13. Contrato inicial con React

El frontend utilizará la API REST como única fuente de información.

El registro deberá solicitar:

- código institucional;
- nombres;
- apellidos;
- fecha de nacimiento;
- fecha de ingreso.

La interfaz de consulta mostrará inicialmente:

- código institucional;
- nombre completo;
- fecha de nacimiento;
- fecha de ingreso;
- estado.

Las acciones de:

- registrar;
- editar;
- activar;
- desactivar;

solo deberán mostrarse a usuarios con capacidad de gestión.

El backend seguirá siendo responsable de autorizar cada operación.

## 14. Validaciones principales

El backend deberá aplicar como mínimo:

- código institucional obligatorio;
- código institucional único;
- código institucional no vacío después de eliminar espacios;
- nombres obligatorios y no vacíos después de eliminar espacios;
- apellidos obligatorios y no vacíos después de eliminar espacios;
- fecha de nacimiento obligatoria;
- fecha de nacimiento no futura;
- fecha de ingreso obligatoria;
- fecha de ingreso no futura;
- fecha de ingreso igual o posterior a la fecha de nacimiento;
- campos automáticos no modificables;
- estado gestionado mediante acciones específicas.

React podrá reproducir algunas validaciones para mejorar la experiencia
del usuario, pero las validaciones definitivas estarán en Django.

## 15. Estrategia de persistencia

No se crearán tablas manualmente mediante SQL.

Django será la fuente de verdad del esquema.

TASK-32 deberá:

1. crear la aplicación apps.students;
2. registrar la aplicación en INSTALLED_APPS;
3. implementar el modelo Student;
4. generar la migración;
5. aplicar la migración sobre SQL Server;
6. verificar la estructura resultante.

## 16. Relación con historias posteriores

Student será la entidad raíz para las siguientes historias:

HU-07 - Expediente individual del estudiante

HU-08 - Consulta y actualización del expediente

HU-09 - Gestión de información familiar

HU-10 - Gestión de documentos del estudiante

Las nuevas entidades deberán relacionarse mediante claves foráneas con
Student sin duplicar la información básica definida en HU-06.

## 17. Principios de diseño

La implementación seguirá estos principios:

- separación de responsabilidades;
- mínimo privilegio;
- no eliminación física de estudiantes;
- validación definitiva en backend;
- React sin acceso directo a la base de datos;
- información sensible separada de la identidad básica;
- migraciones Django como fuente de verdad del esquema;
- reutilización del sistema RBAC implementado previamente.