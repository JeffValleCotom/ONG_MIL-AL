# Seguimiento psicológico — HU-12

## Alcance

HU-12 consolida el seguimiento psicológico de estudiantes dentro de la plataforma MIL-AL.

La implementación se apoya en la estructura psicológica incorporada previamente durante el desarrollo del expediente individual. Para evitar duplicación de funcionalidad, las tareas de HU-12 fueron auditadas contra el código existente antes de introducir cambios.

## TASK-67 — Diseñar estructura del seguimiento psicológico

La estructura ya se encontraba definida mediante `PsychologicalFollowUp`.

El seguimiento contiene:

- estudiante;
- fecha del seguimiento;
- motivo;
- observaciones;
- notas emocionales y conductuales;
- recomendaciones;
- usuario creador;
- usuario de última actualización;
- fechas de creación y actualización.

La información psicológica permanece separada de las áreas académica y terapéutica.

El acceso requiere contexto `PSICOLOGO`, rol correspondiente, asignación profesional activa y permisos funcionales específicos.

No fue necesario crear una nueva estructura.

## TASK-68 — Crear estructura de información psicológica

La estructura persistente ya se encontraba implementada mediante la migración:

`psychology/0001_initial.py`

La migración crea `PsychologicalFollowUp`, sus relaciones protegidas y el índice por estudiante y fecha.

La auditoría confirmó:

- migración aplicada;
- modelo y migración sincronizados;
- ausencia de migraciones pendientes;
- `manage.py check` sin incidencias.

No fue necesario modificar el modelo ni generar una nueva migración.

## TASK-69 — Implementar registro psicológico

El registro ya estaba disponible mediante:

`POST /api/v1/psychological-followups/?context=PSICOLOGO`

El backend ya verificaba:

- contexto `PSICOLOGO`;
- permiso `manage_psychological_followups`;
- asignación activa del psicólogo;
- estudiante activo;
- fecha no futura;
- autoría mediante el usuario autenticado.

El frontend ya contaba con formulario y servicio de registro.

Durante la auditoría se identificó que el expediente no exponía al frontend la capacidad de gestión psicológica.

Se incorporó:

`manage_psychological`

Esta capacidad deriva de `manage_psychological_followups` dentro del contexto `PSICOLOGO`.

El botón para registrar un seguimiento psicológico ahora solo se muestra cuando la capacidad está habilitada y el estudiante está activo.

## TASK-70 — Implementar consulta psicológica

La consulta ya estaba implementada mediante las operaciones `GET` del recurso psicológico y mediante la sección `psychological` del expediente individual.

El backend limita los resultados a:

- contexto `PSICOLOGO`;
- permiso `view_psychological_followups`;
- asignación profesional activa;
- seguimientos creados por el psicólogo autenticado.

No se requirieron cambios adicionales.

## TASK-71 — Implementar actualización psicológica

La actualización ya estaba implementada mediante `PATCH`.

El backend:

- exige `manage_psychological_followups`;
- limita el acceso a seguimientos autorizados;
- impide cambiar el estudiante asociado;
- actualiza `updated_by`;
- no permite eliminación del seguimiento.

El frontend ya disponía del formulario y servicio de actualización.

La nueva capacidad `manage_psychological` también se utiliza para ocultar la acción de edición cuando el usuario conserva consulta pero no gestión.

La API permanece como autoridad final de autorización.

## TASK-72 — Probar seguimiento psicológico

La suite psicológica existente ya cubría registro, consulta, actualización, asignaciones, contextos profesionales, aislamiento entre psicólogos, estudiantes inactivos, fechas futuras y eliminación no permitida.

Para evitar pruebas redundantes se añadieron únicamente escenarios que no estaban cubiertos:

1. un psicólogo con permiso de consulta pero sin `manage_psychological_followups` puede consultar sus seguimientos, pero recibe `403 Forbidden` al intentar actualizarlos;

2. al desactivar la asignación profesional `PSICOLOGO`, los seguimientos dejan de aparecer en la consulta y el detalle devuelve `404 Not Found`;

3. el expediente expone `manage_psychological` de acuerdo con el permiso funcional del rol.

## Validación

Validación integrada de seguimiento psicológico y expediente:

`41 tests`

Resultado:

`OK`

Regresión completa del backend:

`325 tests`

Resultado:

`OK`

Frontend:

`npm.cmd run build`

Resultado:

`built successfully`

`git diff --check` no reportó errores.

## Resultado de HU-12

- TASK-67 — completada mediante auditoría de estructura existente.
- TASK-68 — completada mediante validación de persistencia existente.
- TASK-69 — completada y alineada con capacidad de gestión.
- TASK-70 — completada mediante validación de consulta existente.
- TASK-71 — completada y alineada con autorización de actualización.
- TASK-72 — completada con cobertura adicional únicamente para escenarios faltantes.

HU-12 queda técnicamente completa.
