# Evidencia de pruebas - Gestión de estudiantes

## 1. Identificación

- Feature: FEATURE-02
- Historia de usuario: HU-06 - Registro y gestión de estudiantes
- Tarea: TASK-36 - Probar gestión de estudiantes
- Módulo: Estudiantes
- Backend: Django REST Framework
- Frontend: React
- Base de datos: SQL Server
- Rama de pruebas: `feature/HU-06-task-36-student-management-tests`

## 2. Objetivo

Validar de forma integral las funcionalidades desarrolladas para el
registro y gestión de estudiantes, incluyendo:

- registro;
- consulta;
- búsqueda;
- filtrado;
- actualización;
- activación y desactivación;
- validaciones de datos;
- control de acceso por permisos;
- prevención de eliminación física;
- integración entre frontend, backend y base de datos.

## 3. Reglas funcionales verificadas

La gestión de estudiantes utiliza los permisos:

- `view_students`: permite consultar estudiantes;
- `manage_students`: permite registrar, actualizar y cambiar el estado
  de estudiantes.

La matriz funcional validada para HU-06 es:

| Rol | Consultar | Registrar | Editar | Activar / desactivar |
| --- | --- | --- | --- | --- |
| ADMINISTRADOR | No | No | No | No |
| DOCENTE | Sí | No | No | No |
| PSICOLOGO | Sí | No | No | No |
| TERAPEUTA | Sí | No | No | No |
| RESPONSABLE_INSTITUCIONAL | Sí | Sí | Sí | Sí |

La autorización efectiva se controla en el backend mediante permisos.
La visibilidad de acciones en React funciona únicamente como control
de experiencia de usuario.

## 4. Endpoints verificados

| Método | Endpoint | Permiso | Resultado esperado |
| --- | --- | --- | --- |
| GET | `/api/v1/students/` | `view_students` | Lista estudiantes |
| GET | `/api/v1/students/{id}/` | `view_students` | Consulta estudiante |
| POST | `/api/v1/students/` | `manage_students` | Registra estudiante |
| PATCH | `/api/v1/students/{id}/` | `manage_students` | Actualiza datos |
| PATCH | `/api/v1/students/{id}/activate/` | `manage_students` | Activa estudiante |
| PATCH | `/api/v1/students/{id}/deactivate/` | `manage_students` | Desactiva estudiante |

No se habilitan:

- `PUT /api/v1/students/{id}/`;
- `DELETE /api/v1/students/{id}/`.

La eliminación física de estudiantes no forma parte del diseño de
HU-06.

## 5. Validaciones verificadas

Se comprobó que:

- el código institucional es obligatorio;
- el código institucional se normaliza a mayúsculas;
- el código institucional debe ser único;
- nombres y apellidos son obligatorios;
- la fecha de nacimiento no puede ser futura;
- la fecha de ingreso no puede ser futura;
- la fecha de ingreso no puede ser anterior a la fecha de nacimiento;
- un estudiante se crea activo por defecto;
- `is_active` no puede modificarse mediante el PATCH general;
- los cambios de estado se realizan exclusivamente mediante
  `activate` y `deactivate`;
- activar un estudiante ya activo es una operación idempotente;
- desactivar un estudiante ya inactivo es una operación idempotente.

## 6. Pruebas automatizadas del módulo students

Los tests se encuentran en:

- `backend/apps/students/tests/test_student_registration_api.py`;
- `backend/apps/students/tests/test_student_query_api.py`;
- `backend/apps/students/tests/test_student_update_status_api.py`.

### 6.1 Registro

Resultado:

```text
Ran 10 tests
OK
@'
```

Cobertura:

- registro correcto por `RESPONSABLE_INSTITUCIONAL`;
- normalización del código institucional;
- rechazo de código duplicado;
- rechazo de fecha de nacimiento futura;
- rechazo de fecha de ingreso futura;
- rechazo de fecha de ingreso anterior al nacimiento;
- protección de `is_active` durante el registro;
- rechazo de registro por `DOCENTE`;
- rechazo de registro por `PSICOLOGO`;
- rechazo de registro por `TERAPEUTA`;
- rechazo de registro por `ADMINISTRADOR`;
- rechazo de usuario anónimo.

### 6.2 Consulta

Cobertura automatizada:

- consulta de listado para roles con `view_students`;
- consulta individual;
- búsqueda por código institucional;
- búsqueda por nombres;
- búsqueda por apellidos;
- filtro de estudiantes activos;
- filtro de estudiantes inactivos;
- combinación de búsqueda y estado;
- rechazo de filtro de estado inválido;
- rechazo de `ADMINISTRADOR` sin `view_students`;
- rechazo de usuario anónimo.

### 6.3 Actualización y estado

Cobertura automatizada:

- actualización parcial;
- normalización y unicidad de código durante edición;
- rechazo de fechas inválidas durante edición;
- rechazo de cambio directo de `is_active`;
- desactivación;
- desactivación idempotente;
- activación;
- activación idempotente;
- rechazo de actualización para roles sin `manage_students`;
- rechazo de usuario anónimo;
- rechazo de DELETE;
- rechazo de PUT.

### 6.4 Resultado consolidado del módulo

```text
Ran 33 tests
OK
```

## 7. Regresión completa del proyecto

Se ejecutó:

```powershell
python manage.py test -v 1
```

Resultado:

```text
Ran 157 tests
OK
```

También se ejecutó:

```powershell
python manage.py check
```

Resultado:

```text
System check identified no issues (0 silenced).
```

Se verificaron migraciones pendientes con:

```powershell
python manage.py makemigrations --check --dry-run
```

Resultado:

```text
No changes detected
```

## 8. Validación frontend

Se ejecutó:

```powershell
npm run lint
```

Resultado:

```text
OK
```

Se ejecutó:

```powershell
npm run build
```

Resultado:

```text
vite v8.3.4
40 modules transformed
build completed successfully
```

## 9. Pruebas integradas

Se realizaron pruebas manuales utilizando React, Django y SQL Server.

### Consulta

Un usuario `DOCENTE` pudo:

- acceder al listado de estudiantes;
- buscar por código institucional;
- buscar por nombre;
- filtrar estudiantes;
- limpiar filtros.

El usuario no visualizó:

- formulario de registro;
- acción Editar;
- acción Activar;
- acción Desactivar.

### Registro

Un usuario `RESPONSABLE_INSTITUCIONAL` registró correctamente un
estudiante y el listado se actualizó después de la operación.

Se verificó persistencia en SQL Server.

### Actualización

Se actualizó el estudiante con código:

```text
MIL-T34-001
```

El nombre se modificó a:

```text
Carlos Andrés Manuel
```

La operación se reflejó correctamente en la interfaz y posteriormente
en la base de datos.

### Cambio de estado

Para el mismo estudiante se verificó:

1. desactivación;
2. visualización como inactivo;
3. consulta mediante filtro de inactivos;
4. reactivación;
5. regreso al estado activo.

La consulta final confirmó:

```text
institutional_code: MIL-T34-001
first_name: Carlos Andrés Manuel
last_name: Pérez Gómez
is_active: True
```

## 10. Integridad y control de versiones

Se ejecutó:

```powershell
git diff --check
```

sin errores de formato.

Durante TASK-36 se identificó un hueco de cobertura en las pruebas de
registro para los roles `PSICOLOGO` y `TERAPEUTA`.

Se agregó una prueba automatizada que comprueba que ambos roles reciben
HTTP 403 al intentar registrar estudiantes.

Después del cambio:

```text
Tests de registro: 10 OK
Tests del módulo students: 33 OK
Suite completa: 157 OK
```

## 11. Resultado

HU-06 cumple las verificaciones funcionales y técnicas definidas para:

- registrar estudiantes;
- consultar estudiantes;
- buscar y filtrar estudiantes;
- actualizar datos generales;
- activar y desactivar estudiantes;
- aplicar validaciones de negocio;
- aplicar control de acceso;
- evitar eliminación física;
- persistir correctamente los cambios en SQL Server.

Resultado final de TASK-36:

**APROBADO**