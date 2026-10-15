# Diseño de cambio y recuperación de contraseña

## 1. Objetivo

Definir el proceso seguro para el cambio y recuperación de contraseña
de los usuarios institucionales de la plataforma ONG MIL-AL.

La solución debe permitir:

- Cambiar la contraseña cuando el usuario posee una sesión autenticada.
- Recuperar la contraseña cuando el usuario no puede autenticarse.
- Aplicar las políticas de validación de contraseña definidas por Django.
- Evitar la exposición de información sobre usuarios registrados.
- Utilizar mecanismos de generación y validación de tokens proporcionados
  por Django.
- Mantener la autorización institucional separada del proceso de
  autenticación.

## 2. Principios de seguridad

Las contraseñas nunca deben almacenarse ni transmitirse en texto plano
fuera del proceso necesario para establecer una nueva contraseña.

La aplicación utilizará los mecanismos de hashing proporcionados por
Django mediante `set_password()`.

La validación de nuevas contraseñas utilizará
`django.contrib.auth.password_validation.validate_password()`.

La recuperación de contraseña utilizará tokens temporales generados por
Django mediante `PasswordResetTokenGenerator`.

No se implementarán algoritmos criptográficos ni tokens personalizados.

Los endpoints que modifiquen contraseñas mediante una sesión autenticada
estarán protegidos por CSRF.

El proceso de recuperación no revelará si una dirección de correo
electrónico pertenece o no a un usuario registrado.

## 3. Cambio de contraseña

### 3.1 Requisitos

El usuario debe:

1. Poseer una sesión autenticada y activa.
2. Proporcionar su contraseña actual.
3. Proporcionar la nueva contraseña.
4. Confirmar la nueva contraseña.
5. Cumplir las reglas de validación de contraseña configuradas en Django.

### 3.2 Endpoint propuesto

```text
POST /api/v1/auth/password/change/
```

Entrada:

```json
{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña",
  "new_password_confirm": "nueva_contraseña"
}
```

Respuesta exitosa:

```text
200 OK
```

El backend verificará la contraseña actual mediante `check_password()`.

Si la validación es correcta, la nueva contraseña se establecerá
mediante `set_password()`.

Después del cambio se utilizará `update_session_auth_hash()` para
mantener válida la sesión actual del usuario.

El cambio del hash de autenticación invalidará las demás sesiones que ya
no coincidan con el nuevo hash de contraseña.

## 4. Recuperación de contraseña

La recuperación se realizará mediante la posesión del correo electrónico
registrado y de un token temporal de recuperación.

No se utilizarán preguntas de seguridad.

### 4.1 Solicitud de recuperación

Endpoint propuesto:

```text
POST /api/v1/auth/password/recovery/request/
```

Entrada:

```json
{
  "email": "usuario@institucion.com"
}
```

La respuesta será genérica independientemente de que el correo exista:

```text
200 OK
```

Ejemplo conceptual:

```json
{
  "detail": "Si existe una cuenta asociada, se enviarán instrucciones de recuperación."
}
```

Esto evita permitir la enumeración de usuarios registrados.

Si existe un usuario válido y activo asociado al correo, el backend
generará:

```text
uid
token
```

El `uid` identificará al usuario mediante una representación segura para
URL.

El `token` será generado mediante `PasswordResetTokenGenerator`.

Estos datos serán enviados al correo registrado del usuario mediante un
enlace de recuperación.

## 5. Verificación de identidad

La verificación de identidad para recuperación se basará en dos factores
del flujo:

```text
posesión del correo registrado
+
token temporal válido
```

Endpoint propuesto:

```text
POST /api/v1/auth/password/recovery/verify/
```

Entrada:

```json
{
  "uid": "...",
  "token": "..."
}
```

El backend verificará:

```text
usuario existente
usuario activo
uid válido
token válido
token no expirado
```

Un superusuario técnico de Django no tendrá un mecanismo especial de
recuperación diferente al resto de usuarios.

La validez del token será determinada por Django y por el tiempo de
expiración configurado para los tokens de recuperación.

## 6. Confirmación de recuperación

Endpoint propuesto:

```text
POST /api/v1/auth/password/recovery/confirm/
```

Entrada:

```json
{
  "uid": "...",
  "token": "...",
  "new_password": "nueva_contraseña",
  "new_password_confirm": "nueva_contraseña"
}
```

Antes de modificar la contraseña, el backend volverá a verificar el token.

La nueva contraseña deberá cumplir las mismas reglas de validación
utilizadas durante el cambio de contraseña autenticado.

La contraseña será actualizada mediante:

```text
user.set_password(...)
user.save(...)
```

Una vez modificada la contraseña, el token utilizado dejará de ser válido
debido al cambio del estado de autenticación del usuario.

## 7. Validación de contraseñas

El backend utilizará las políticas configuradas en:

```text
AUTH_PASSWORD_VALIDATORS
```

No se duplicarán manualmente estas reglas en los serializers.

La validación deberá cubrir, como mínimo, las políticas configuradas por
Django para el proyecto.

Los mensajes de validación serán transformados en respuestas HTTP 400
comprensibles para el cliente.

La contraseña y su confirmación deberán coincidir antes de efectuar
cualquier modificación.

## 8. Códigos HTTP esperados

```text
200 OK
Cambio, solicitud, verificación o recuperación realizada correctamente.

400 Bad Request
Datos inválidos, contraseñas diferentes, contraseña actual incorrecta,
token inválido o contraseña que no cumple las políticas.

401/403
Usuario no autenticado o sin una sesión válida cuando intenta utilizar
el cambio de contraseña autenticado.
```

Los endpoints públicos de recuperación no requerirán una sesión
autenticada.

## 9. Roles y permisos

El cambio de contraseña pertenece al propio usuario y no dependerá de su
rol institucional.

Un usuario DOCENTE, PSICOLOGO, TERAPEUTA,
RESPONSABLE_INSTITUCIONAL o ADMINISTRADOR podrá cambiar su propia
contraseña si posee una sesión válida.

Los permisos funcionales de HU-04 no otorgarán capacidad para conocer ni
establecer directamente la contraseña de otro usuario.

La recuperación tampoco dependerá de un rol institucional porque ocurre
antes de la autenticación.

## 10. Integración con el frontend

El frontend React consumirá los endpoints mediante el cliente HTTP
existente.

El cambio de contraseña autenticado utilizará el mecanismo CSRF ya
implementado en el cliente API.

La interfaz nunca almacenará la contraseña actual, la nueva contraseña ni
los tokens de recuperación en almacenamiento persistente del navegador.

La autorización real continuará siendo responsabilidad del backend.

## 11. Responsabilidades por Task

TASK-25 define el presente diseño.

TASK-26 implementará el cambio de contraseña para usuarios autenticados.

TASK-27 implementará y verificará la política de validación de nuevas
contraseñas.

TASK-28 implementará la solicitud y envío del proceso de recuperación.

TASK-29 implementará la validación del uid y token utilizados para
verificar la identidad durante la recuperación.

TASK-30 implementará las pruebas de aceptación del flujo completo de
cambio y recuperación de contraseña.