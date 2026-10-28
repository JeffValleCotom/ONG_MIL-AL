# Tipos de documentos del estudiante

## 1. Objetivo

Este documento define el catálogo funcional de tipos de documentos que podrán asociarse a un estudiante en HU-10 - Gestión de documentos del estudiante.

La clasificación definida aquí será utilizada posteriormente para diseñar el almacenamiento, carga, consulta, descarga y validación de documentos.

Esta tarea no define todavía la ubicación física de los archivos ni implementa modelos, endpoints o interfaces.

## 2. Principios

La gestión documental seguirá los principios generales definidos para el expediente del estudiante:

- cada documento pertenecerá a un único estudiante;
- Student continuará siendo la entidad raíz;
- los documentos se gestionarán mediante una entidad independiente;
- no se duplicará información básica del estudiante dentro de la estructura documental;
- la clasificación será controlada y no dependerá de texto libre;
- el backend será la autoridad para validar el tipo documental;
- la clasificación de un documento no otorgará por sí misma permisos de acceso;
- los documentos sensibles deberán respetar las restricciones de acceso del dominio al que pertenecen;
- la estructura deberá permitir conservar documentos históricos.

## 3. Catálogo de tipos

Se utilizarán códigos estables para identificar cada tipo de documento.

| Código | Nombre | Finalidad |
| --- | --- | --- |
| `IDENTIFICACION` | Documento de identificación | Documentos utilizados para identificar al estudiante cuando sean necesarios para procesos institucionales. |
| `CONSENTIMIENTO_AUTORIZACION` | Consentimiento o autorización | Consentimientos informados, autorizaciones de responsables u otros documentos que acrediten autorización para procesos institucionales. |
| `ACADEMICO` | Documento académico | Reportes, constancias, evaluaciones, certificados u otros documentos relacionados con el seguimiento académico. |
| `MEDICO` | Documento médico | Informes, constancias u otros documentos de carácter médico aportados para el expediente del estudiante. |
| `PSICOLOGICO` | Documento psicológico | Informes, evaluaciones u otros documentos pertenecientes al ámbito psicológico. |
| `TERAPEUTICO` | Documento terapéutico | Informes, evaluaciones u otros documentos pertenecientes al seguimiento terapéutico. |
| `INSTITUCIONAL` | Documento institucional | Formularios, constancias, comunicaciones u otros documentos administrativos propios de la ONG. |
| `OTRO` | Otro documento | Documento que no corresponde a ninguno de los tipos anteriores. |

## 4. Identificadores internos

Los códigos del catálogo son los valores que utilizará el sistema internamente.

Los nombres visibles podrán presentarse en español en la interfaz, pero el código almacenado deberá mantenerse estable.

Ejemplo:

```text
ACADEMICO -> Documento académico
PSICOLOGICO -> Documento psicológico
```

No se utilizarán nombres escritos libremente como sustituto del código del tipo documental.

## 5. Tipo OTRO

`OTRO` se utilizará únicamente cuando el documento no pueda clasificarse mediante uno de los tipos definidos.

Cuando se seleccione `OTRO`, deberá proporcionarse posteriormente una descripción específica que indique la naturaleza del documento.

Para los demás tipos, esa descripción específica no será obligatoria como parte de la clasificación.

Esta regla deberá ser validada definitivamente por el backend cuando se implemente la carga documental.

## 6. Multiplicidad

Un estudiante podrá tener múltiples documentos del mismo tipo.

Por ejemplo, podrán existir:

- varios documentos académicos correspondientes a distintos periodos;
- varios informes psicológicos elaborados en fechas diferentes;
- varios documentos terapéuticos;
- diferentes autorizaciones o consentimientos;
- múltiples documentos institucionales.

Por lo tanto, el tipo documental no será único por estudiante.

## 7. Obligatoriedad

HU-10 no establecerá que alguno de los tipos del catálogo sea obligatorio para todos los estudiantes.

La ausencia de un determinado documento no impedirá por sí misma la existencia o consulta del estudiante.

Si posteriormente un proceso institucional requiere un documento específico, dicha obligatoriedad deberá implementarse como una regla de negocio independiente y no como una propiedad global del catálogo.

## 8. Clasificación de sensibilidad

Los tipos documentales pueden contener distintos niveles de sensibilidad.

### Documentos de carácter institucional o general

Incluyen principalmente:

- `IDENTIFICACION`
- `CONSENTIMIENTO_AUTORIZACION`
- `ACADEMICO`
- `INSTITUCIONAL`
- `OTRO`, según su contenido

### Documentos sensibles por dominio

Incluyen:

- `MEDICO`
- `PSICOLOGICO`
- `TERAPEUTICO`

La pertenencia de un documento a una categoría no implica que todos los usuarios que puedan consultar al estudiante puedan acceder al archivo.

La autorización deberá evaluarse independientemente y será definida en las tareas posteriores de HU-10 reutilizando el sistema RBAC existente.

Especialmente, los documentos psicológicos y terapéuticos no deberán exponerse automáticamente a otros perfiles únicamente porque tengan acceso al expediente general del estudiante.

## 9. Relación con información familiar

HU-09 excluyó expresamente el almacenamiento de documentos de identificación y otra documentación adicional dentro de la estructura de información familiar.

HU-10 será responsable de la documentación asociada al estudiante.

Por lo tanto, los archivos no se almacenarán directamente dentro de `StudentFamilyMember`.

Si un documento está relacionado con un proceso familiar o una autorización, continuará siendo un documento del estudiante y se clasificará mediante el catálogo definido en HU-10.

## 10. Datos que no forman parte del tipo documental

El catálogo únicamente clasifica la naturaleza del documento.

No forman parte de la definición del tipo:

- nombre físico del archivo;
- ruta de almacenamiento;
- extensión;
- tipo MIME;
- tamaño;
- usuario que realizó la carga;
- fecha de carga;
- estado activo o histórico;
- descripción del documento;
- mecanismos de descarga;
- hash o mecanismos de integridad.

Estos aspectos serán definidos en TASK-56 - Diseñar almacenamiento de documentos y en las tareas posteriores de HU-10.

## 11. Reglas funcionales del catálogo

El catálogo deberá cumplir las siguientes reglas:

1. Todo documento deberá pertenecer a un tipo válido.
2. Los códigos serán controlados por el backend.
3. No se aceptarán tipos arbitrarios enviados por el cliente.
4. Un estudiante podrá poseer múltiples documentos del mismo tipo.
5. `OTRO` permitirá representar documentos no contemplados inicialmente.
6. `OTRO` requerirá una descripción específica del tipo de documento.
7. La clasificación no otorgará permisos de consulta o descarga.
8. Los documentos sensibles deberán conservar las restricciones correspondientes a su dominio.
9. La creación de un nuevo tipo en el futuro deberá realizarse modificando explícitamente el catálogo.
10. La interfaz React utilizará los valores suministrados o admitidos por el backend y no será la autoridad de validación.

## 12. Decisiones fuera del alcance de TASK-55

TASK-55 no define:

- si los archivos se almacenarán en el sistema de archivos, almacenamiento externo o algún otro mecanismo;
- la estructura de directorios;
- el nombre físico de los archivos;
- límites de tamaño;
- formatos permitidos;
- extensiones permitidas;
- validaciones MIME;
- mecanismos de descarga;
- eliminación o desactivación de documentos;
- versionamiento;
- endpoints;
- permisos funcionales concretos;
- interfaz de carga.

Estas decisiones corresponden principalmente a TASK-56, TASK-57, TASK-58 y TASK-59.

## 13. Catálogo definitivo de TASK-55

Los valores definidos para HU-10 son:

```text
IDENTIFICACION
CONSENTIMIENTO_AUTORIZACION
ACADEMICO
MEDICO
PSICOLOGICO
TERAPEUTICO
INSTITUCIONAL
OTRO
```

Este catálogo constituye la base funcional para el diseño de almacenamiento documental de TASK-56.

La arquitectura de almacenamiento, metadatos, conservación histórica e
integridad de los archivos se define en
`docs/architecture/student-document-storage.md`.
