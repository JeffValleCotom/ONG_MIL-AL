# Almacenamiento de documentos del estudiante

## 1. Objetivo

Este documento define la arquitectura de almacenamiento para HU-10 - Gestión de documentos del estudiante.

El diseño establece:

- separación entre metadatos y contenido físico;
- estructura lógica del registro documental;
- ubicación privada de los archivos;
- generación segura de nombres físicos;
- conservación del nombre original;
- trazabilidad y auditoría;
- integridad mediante hash;
- conservación histórica;
- reglas de consistencia entre base de datos y almacenamiento.

La carga, consulta, descarga y validaciones concretas se implementarán en las tareas posteriores de HU-10.

## 2. Decisión de almacenamiento

Los documentos no se almacenarán como contenido binario dentro de SQL Server.

SQL Server almacenará exclusivamente los metadatos necesarios para identificar, clasificar, auditar y localizar cada documento.

El contenido físico del archivo se almacenará mediante el sistema de almacenamiento de Django.

Para el entorno actual del proyecto se utilizará almacenamiento privado en el sistema de archivos del servidor.

La arquitectura deberá utilizar la abstracción de almacenamiento de Django para permitir que, en un despliegue futuro, el almacenamiento físico pueda sustituirse por un servicio externo sin modificar la lógica de negocio principal.

## 3. Separación de responsabilidades

La solución tendrá dos componentes independientes.

### Base de datos

La base de datos conservará información como:

- estudiante propietario;
- tipo documental;
- detalle del tipo cuando corresponda;
- nombre original;
- referencia relativa al archivo almacenado;
- tipo MIME declarado o validado;
- tamaño;
- hash de integridad;
- descripción;
- estado;
- auditoría;
- fechas de creación, actualización y desactivación.

### Almacenamiento físico

El almacenamiento conservará únicamente el contenido binario del documento.

No contendrá lógica de autorización ni será consultado directamente por React.

La autorización seguirá siendo responsabilidad del backend Django.

## 4. Entidad documental

Se diseñará una entidad independiente denominada conceptualmente `StudentDocument`.

Cada registro representará un documento asociado a un único `Student`.

La relación será:

```text
Student 1 ---- N StudentDocument
```

Un estudiante podrá tener cero, uno o múltiples documentos.

También podrá tener múltiples documentos del mismo tipo.

No se duplicarán en `StudentDocument` nombres, apellidos u otros datos personales que ya pertenezcan a `Student`.

## 5. Metadatos previstos

La estructura documental deberá contemplar como mínimo los siguientes datos:

| Campo conceptual | Tipo | Propósito |
| --- | --- | --- |
| `id` | Identificador | Identificador interno del registro documental. |
| `student` | FK → Student | Estudiante propietario del documento. |
| `document_type` | Código controlado | Tipo definido en el catálogo de TASK-55. |
| `document_type_detail` | Texto opcional | Descripción específica requerida cuando el tipo sea `OTRO`. |
| `original_filename` | Texto | Nombre que poseía el archivo al ser cargado. |
| `file` | Referencia de almacenamiento | Ruta o clave relativa administrada por Django. |
| `mime_type` | Texto | Tipo MIME asociado al documento. |
| `size_bytes` | Entero | Tamaño del archivo en bytes. |
| `sha256` | Texto hexadecimal | Huella SHA-256 del contenido almacenado. |
| `description` | Texto opcional | Descripción funcional del documento. |
| `is_active` | Booleano | Indica si el documento continúa vigente dentro del expediente. |
| `deactivated_at` | Fecha y hora opcional | Momento de desactivación lógica. |
| `created_by` | FK → User | Usuario que realizó la carga. |
| `updated_by` | FK → User | Usuario que realizó la última modificación de metadatos o estado. |
| `created_at` | Fecha y hora | Momento de creación del registro. |
| `updated_at` | Fecha y hora | Momento de la última actualización. |

Los tipos exactos de campos Django serán definidos cuando se implemente el modelo.

## 6. Nombre original y nombre físico

El nombre enviado por el usuario no será utilizado directamente como nombre físico del archivo.

Por ejemplo, un archivo cargado como:

```text
Informe psicológico marzo 2026.pdf
```

podrá conservar ese valor en:

```text
original_filename
```

pero deberá almacenarse físicamente con un identificador generado por el servidor.

Ejemplo conceptual:

```text
cb615ef7-02e5-43f8-a559-60ec9dc02925.pdf
```

Esto evita:

- colisiones entre nombres;
- sobrescritura accidental;
- dependencia de nombres proporcionados por usuarios;
- caracteres problemáticos;
- exposición innecesaria de información personal en la ruta física.

`original_filename` deberá conservar únicamente el nombre base y nunca una ruta proporcionada por el cliente.

## 7. Identificador físico

El nombre físico utilizará un UUID generado por el backend.

No se utilizarán como identificador físico:

- nombre del estudiante;
- DPI u otro identificador personal;
- correo electrónico;
- nombre original completo;
- nombre del usuario que carga el archivo.

El UUID será independiente del identificador de base de datos.

## 8. Extensión

Cuando sea necesario conservar una extensión en el nombre físico, esta deberá provenir de un valor previamente normalizado y validado.

La extensión enviada en el nombre original no se considerará suficiente para determinar el tipo real del contenido.

Las reglas concretas de extensiones y MIME permitidos corresponden a TASK-59 - Implementar validaciones de documentos.

## 9. Estructura de almacenamiento

En el entorno local se utilizará una raíz privada conceptual:

```text
backend/private_media/
```

Los archivos se organizarán conceptualmente mediante:

```text
students/{student_id}/documents/{year}/{month}/{uuid}.{extension}
```

Ejemplo:

```text
students/42/documents/2026/10/cb615ef7-02e5-43f8-a559-60ec9dc02925.pdf
```

La ruta almacenada en la base de datos será relativa al almacenamiento configurado.

No se almacenarán rutas absolutas como:

```text
C:\Users\...
```

ni rutas dependientes de una estación de trabajo concreta.

## 10. Razón para no utilizar el tipo documental en la ruta

El tipo documental no formará parte de la estructura física de directorios.

Por ejemplo, no se utilizará:

```text
students/42/PSICOLOGICO/...
```

El tipo pertenece a los metadatos del registro.

Esta separación evita que una eventual corrección de clasificación obligue a mover físicamente el archivo.

Por lo tanto, cambiar metadatos no deberá modificar innecesariamente la ubicación del contenido físico.

## 11. Configuración privada

El almacenamiento documental no deberá utilizarse como un directorio público servido directamente por el frontend.

Se prevé una configuración conceptual similar a:

```text
PRIVATE_MEDIA_ROOT = backend/private_media
```

La ubicación definitiva se configurará desde Django y podrá ser parametrizable mediante variables de entorno.

No se expondrá una `MEDIA_URL` pública para estos documentos sensibles.

## 12. Descarga controlada

React nunca accederá directamente a la ruta física del archivo.

La descarga deberá realizarse posteriormente mediante un endpoint autenticado del backend.

El flujo conceptual será:

```text
React
  |
  | solicitud autenticada
  v
Django
  |
  | autorización RBAC + contexto
  v
StudentDocument
  |
  | referencia privada
  v
Storage
```

Solo después de comprobar la autorización Django podrá entregar el contenido.

La ruta física o clave interna no deberá utilizarse como mecanismo de autorización.

## 13. Protección de documentos sensibles

Los tipos definidos en TASK-55 incluyen documentos con distintos niveles de sensibilidad.

En particular:

- `MEDICO`;
- `PSICOLOGICO`;
- `TERAPEUTICO`.

El almacenamiento físico será privado para todos los tipos, no únicamente para los sensibles.

La diferencia de acceso se resolverá en la capa de autorización del backend.

No se crearán carpetas públicas diferentes por rol.

## 14. Política para OTRO

`OTRO` continuará requiriendo `document_type_detail`.

El hecho de utilizar `OTRO` no permitirá evitar las reglas de seguridad.

Cuando el contenido pertenezca realmente a un dominio sensible, deberá aplicarse la política de autorización correspondiente.

La clasificación no será utilizada para disminuir automáticamente la protección de un archivo.

## 15. Hash de integridad

Cada archivo almacenado tendrá una huella SHA-256 calculada por el backend.

El valor se almacenará en el campo conceptual:

```text
sha256
```

La huella permitirá:

- comprobar la integridad del contenido;
- detectar modificaciones inesperadas;
- facilitar diagnósticos de archivos duplicados;
- mantener evidencia técnica sobre el contenido originalmente almacenado.

El hash no contendrá el archivo y no sustituirá el almacenamiento físico.

## 16. Duplicados

Dos registros podrán tener el mismo hash.

Por lo tanto:

```text
sha256
```

no tendrá una regla de unicidad global.

Pueden existir casos legítimos en los que el mismo documento se cargue en contextos distintos o se conserve como parte de diferentes registros.

La detección de coincidencias no implicará automáticamente rechazo.

## 17. Tamaño

El tamaño real del archivo se almacenará en bytes mediante:

```text
size_bytes
```

Esto permitirá:

- mostrar información del documento;
- realizar controles posteriores;
- auditar archivos;
- aplicar límites de tamaño durante la validación.

TASK-56 no define todavía el límite máximo permitido.

El límite concreto será establecido en TASK-59.

## 18. Tipo MIME

El sistema conservará un valor de tipo MIME asociado al archivo.

El valor enviado por el navegador no será considerado automáticamente confiable.

La estrategia de validación entre extensión, MIME declarado y contenido será definida en TASK-59.

## 19. Estado e historial

Los documentos tendrán estado lógico.

Un registro activo tendrá:

```text
is_active = true
deactivated_at = null
```

Un documento desactivado tendrá:

```text
is_active = false
deactivated_at = fecha y hora de desactivación
```

La desactivación no eliminará automáticamente el archivo físico.

## 20. No eliminación física

HU-10 conservará historial documental.

No se realizará eliminación física de un documento como operación normal de usuario.

Cuando un documento deje de estar vigente se utilizará desactivación lógica.

Esto conservará:

- metadatos;
- archivo físico;
- autor de la carga;
- fechas;
- hash;
- trazabilidad histórica.

Una política administrativa futura de retención o eliminación definitiva deberá diseñarse explícitamente y no formará parte de las operaciones normales de HU-10.

## 21. Corrección de metadatos

Los metadatos permitidos podrán corregirse posteriormente sin sustituir automáticamente el archivo físico.

Por ejemplo, podrá corregirse:

- clasificación;
- detalle de `OTRO`;
- descripción.

No deberá modificarse manualmente:

- hash del contenido;
- tamaño real;
- referencia física generada;
- usuario creador;
- fecha original de carga.

Si se requiere sustituir el contenido físico, deberá tratarse como un nuevo documento y conservarse el anterior como histórico.

## 22. Versionamiento

HU-10 no implementará inicialmente una cadena formal de versiones mediante campos como:

```text
version
previous_version
```

Cada carga será un registro documental independiente.

La relación temporal podrá reconstruirse mediante:

- tipo;
- estudiante;
- fechas;
- estado;
- descripción.

Si posteriormente se requiere versionamiento documental explícito, podrá incorporarse como una ampliación del modelo.

## 23. Auditoría

Todo documento deberá conservar como mínimo:

```text
created_by
updated_by
created_at
updated_at
```

La carga identificará al usuario autenticado responsable de crear el registro.

La actualización de metadatos o estado actualizará `updated_by`.

Estos valores serán establecidos por el backend y no serán aceptados libremente desde React.

## 24. Consistencia entre archivo y base de datos

La creación documental involucra dos recursos distintos:

1. almacenamiento físico;
2. base de datos.

La implementación deberá evitar registros incompletos y archivos huérfanos.

Si el archivo se almacena físicamente pero la creación del registro en base de datos falla, el backend deberá intentar eliminar el archivo recién creado como compensación.

No deberá existir un registro confirmado que haga referencia a un archivo que nunca fue almacenado correctamente.

Estas reglas serán aplicadas durante TASK-57.

## 25. Colisiones

Los nombres físicos basados en UUID reducen la posibilidad de colisiones.

Aun así, el almacenamiento de Django continuará siendo la autoridad para resolver el nombre final utilizado.

Nunca se sobrescribirá deliberadamente un documento existente por coincidir con el nombre original proporcionado por el usuario.

## 26. Base de datos

SQL Server almacenará únicamente la referencia relativa al archivo.

Ejemplo conceptual:

```text
students/42/documents/2026/10/cb615ef7-02e5-43f8-a559-60ec9dc02925.pdf
```

No almacenará:

- el contenido binario completo;
- una ruta absoluta del sistema operativo;
- una URL pública de descarga.

Esto mantiene separada la persistencia relacional del almacenamiento de objetos binarios.

## 27. Portabilidad

La lógica de negocio no dependerá directamente de operaciones específicas de Windows como:

```text
C:\
```

ni deberá abrir archivos concatenando rutas manualmente desde vistas o serializers.

Las operaciones deberán realizarse mediante la abstracción de almacenamiento utilizada por Django.

Esto permitirá ejecutar el backend posteriormente en otros sistemas operativos o migrar a un proveedor de almacenamiento diferente.

## 28. Control de versiones Git

El contenido de:

```text
backend/private_media/
```

no deberá formar parte del repositorio Git.

Los archivos cargados por usuarios son datos operativos y no código fuente.

Antes de habilitar la carga documental, la ruta correspondiente deberá quedar excluida mediante `.gitignore`.

## 29. Respaldos

Los documentos físicos y sus metadatos forman conjuntamente el expediente documental.

Un respaldo completo deberá considerar:

- base de datos SQL Server;
- almacenamiento privado de documentos.

Respaldar solamente la base de datos no será suficiente para recuperar los archivos.

De igual manera, respaldar solamente los archivos no permitirá reconstruir correctamente clasificación, auditoría y relaciones.

La estrategia operativa de copias de seguridad queda fuera de la implementación directa de HU-10, pero la arquitectura deberá permitirla.

## 30. Seguridad de nombres

El backend no confiará en rutas proporcionadas por el cliente.

El cliente únicamente enviará el archivo y los metadatos funcionales permitidos.

El backend generará la referencia física.

No se aceptarán desde React valores destinados a controlar:

```text
file_path
storage_path
upload_to
```

Esto evita que el cliente determine ubicaciones arbitrarias dentro del servidor.

## 31. Registro inactivo y archivo físico

Cuando un documento sea desactivado:

```text
is_active = false
```

el archivo físico permanecerá almacenado.

Un documento histórico no deberá convertirse en inaccesible por inexistencia física.

Las consultas normales podrán diferenciar documentos vigentes e históricos mediante metadatos.

## 32. Relación con Student

La propiedad documental se determinará exclusivamente mediante la relación con `Student`.

No se crearán copias independientes del archivo dentro de:

- seguimiento académico;
- seguimiento psicológico;
- seguimiento terapéutico;
- información familiar.

Los distintos dominios podrán referirse funcionalmente al documento, pero la entidad documental seguirá perteneciendo al expediente del estudiante.

## 33. Cambios de estado del estudiante

La desactivación de un estudiante no eliminará sus documentos.

El expediente histórico deberá permanecer íntegro.

Las reglas sobre posibilidad de cargar nuevos documentos para estudiantes inactivos se definirán en las tareas funcionales posteriores y no mediante el sistema de almacenamiento.

## 34. Exclusiones de TASK-56

TASK-56 no implementa todavía:

- modelo Django definitivo;
- migración;
- formulario de carga;
- endpoint de carga;
- endpoint de descarga;
- permisos funcionales concretos;
- límites máximos de tamaño;
- extensiones permitidas;
- inspección MIME;
- antivirus;
- interfaz React;
- eliminación física.

Estas responsabilidades corresponden a TASK-57, TASK-58 y TASK-59.

## 35. Decisiones definitivas de TASK-56

La arquitectura documental adopta las siguientes decisiones:

1. Los archivos físicos no se almacenarán como binarios en SQL Server.
2. SQL Server conservará los metadatos y la referencia relativa al archivo.
3. Los archivos se almacenarán de forma privada mediante la abstracción de almacenamiento de Django.
4. El entorno local utilizará conceptualmente `backend/private_media/`.
5. No existirá una URL pública directa para los documentos.
6. React nunca accederá directamente al sistema de archivos.
7. Las descargas pasarán por autorización del backend.
8. Los nombres físicos utilizarán UUID.
9. El nombre original se conservará únicamente como metadato.
10. La estructura física será `students/{student_id}/documents/{year}/{month}/{uuid}.{extension}`.
11. El tipo documental no formará parte de la ruta física.
12. Cada archivo tendrá tamaño y hash SHA-256 almacenados como metadatos.
13. El hash no será único.
14. Los documentos serán desactivados lógicamente y conservarán su archivo físico.
15. La sustitución de contenido se representará mediante un nuevo registro.
16. Los documentos físicos quedarán fuera de Git.
17. El backend será la única autoridad para construir rutas y controlar acceso.
18. La arquitectura permanecerá desacoplada del proveedor físico de almacenamiento.
