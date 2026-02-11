# ESPECIFICACIÓN: Sistema de Autenticación

**Estado:** ⚪ BORRADOR
**Referencia:** feat/authentication
**Versión:** 1.0

## 1. Contexto ("El Porqué")

Los usuarios necesitan crear cuentas y autenticarse de forma segura para acceder a los recursos protegidos de la API. El sistema debe soportar autenticación tradicional con usuario/contraseña y autenticación mediante Google OAuth para reducir fricción en el proceso de registro y proporcionar opciones flexibles de acceso.

### 1.1 Métricas de Éxito (KPIs)

* [ ] **Seguridad:** 100% de contraseñas almacenadas con hashing bcrypt (cost 12)
* [ ] **Tiempo de respuesta:** Login y registro completados en menos de 500ms
* [ ] **Adopción:** Al menos 30% de usuarios utilizan Google OAuth

### 1.2 Fuera de Alcance (Out of Scope)

* [ ] No se contempla recuperación de contraseña (reset password)
* [ ] No se contempla autenticación de dos factores (2FA)
* [ ] Soporte para otros proveedores OAuth (Facebook, Apple, GitHub)
* [ ] Refresh tokens (solo access tokens JWT)

## 2. Requisitos Funcionales (Sintaxis EARS)

### R1: Registro de Usuario con Credenciales

* **Regla:** CUANDO un usuario envía datos de registro (email, password, username opcional), EL SISTEMA DEBE validar que el **email** sea único y crear una cuenta con contraseña hasheada.
* **Regla:** CUANDO el **email** ya existe en la base de datos, EL SISTEMA DEBE retornar error 409 Conflict.
* **Regla:** CUANDO la contraseña no cumple requisitos mínimos (8+ caracteres), EL SISTEMA DEBE retornar error 400 Bad Request.
* **Restricción:** **Email** debe ser único y tener formato válido.
* **Restricción:** Password debe tener mínimo 8 caracteres.
* **Nota:** El `username` es meramente decorativo (display name), NO es único y NO se usa para login.

### R2: Login con Credenciales

* **Regla:** CUANDO un usuario envía credenciales válidas (**email**, password), EL SISTEMA DEBE generar un **Access Token (PASETO)** de corta duración (15 min) y un **Refresh Token** de larga duración (7 días).
* **Regla:** El Access Token DEBE retornarse en el cuerpo de la respuesta o header, y el Refresh Token DEBE setearse en una **Cookie HttpOnly, Secure, SameSite=None**.
* **Regla:** CUANDO las credenciales son inválidas, EL SISTEMA DEBE retornar error 401 Unauthorized.

### R3: Login con Google OAuth

* **Regla:** CUANDO un usuario envía un Google ID Token válido, EL SISTEMA DEBE autenticar/crear el usuario y retornar el par de tokens (Access + Refresh) igual que en R2.
* **Regla:** CUANDO el Google ID Token es inválido o expirado, EL SISTEMA DEBE retornar error 401 Unauthorized.

### R4: Protección de Recursos

* **Regla:** CUANDO una request incluye un Access Token válido (PASETO) en header `Authorization: Bearer {token}`, EL SISTEMA DEBE permitir acceso.
* **Regla:** CUANDO el Access Token ha expirado, el cliente DEBE poder usar el endpoint `/auth/refresh` enviando la cookie de Refresh Token para obtener un nuevo par de tokens.

### R5: Refresco de Tokens (Refresh Token Rotation)

* **Regla:** CUANDO se usa un Refresh Token válido, el sistema DEBE invalidarlo (rotarlo), generar un nuevo par (Access + Refresh) y actualizar la cookie.
* **Regla:** CUANDO se intenta usar un Refresh Token ya invalidado/usado, el sistema DEBE invalidar toda la cadena de tokens del usuario (detección de robo) y forzar re-login.

### 2.6 Estándar de Errores (RFC 7807)

* **Regla:** TODAS las respuestas de error (4xx, 5xx) DEBEN seguir el estándar **Problem Details for HTTP APIs** (RFC 7807).
* **Formato:**
  ```json
  {
    "type": "about:blank",
    "title": "Descripción corta del error",
    "status": 400,
    "detail": "Descripción detallada legible por humanos",
    "instance": "/path/to/resource"
  }
  ```
* **Códigos Específicos:**
  - `400 Bad Request`: Datos de entrada inválidos o malformados.
  - `401 Unauthorized`: Credenciales inválidas (`invalid_credentials`) o token expirado/faltante.
  - `409 Conflict`: Recurso duplicado (`user_already_exists`).
  - `500 Internal Server Error`: Errores no controlados.

## 3. Criterios de Aceptación (Verificación)

* [ ] Implementación de **PASETO v4** (Local) para tokens
* [ ] **Refresh Token Rotation** implementado y funcional
* [ ] Login retorna Access Token (Body) y Refresh Token (Cookie HttpOnly)
* [ ] Endpoint `/auth/refresh` renueva tokens correctamente usando la cookie
* [ ] **CORS** configurado para permitir credenciales (cookies)
* [ ] Cookies configuradas con `Secure`, `HttpOnly`, `SameSite=None`
* [ ] Usuario puede registrarse/login con Email
* [ ] Login con Google OAuth funcional
* [ ] Middleware valida PASETO tokens correctamente

## 4. Casos Borde (Edge Cases)

* [ ] **Email inválido:** Retornar 400 Bad Request
* [ ] **Password vacía:** Retornar 400 Bad Request
* [ ] **JWT expirado:** Retornar 401
* [ ] **JWT malformado:** Retornar 401
* [ ] **Google token revocado:** Retornar 401 con mensaje descriptivo
* [ ] **Header Authorization sin prefijo Bearer:** Retornar 401
* [ ] **Email de Google sin verificar:** Aceptar de todas formas (Google lo maneja)

## 5. Casos de Uso de Negocio (End-to-End)

Esta sección detalla los flujos soportados por la aplicación, tanto los caminos felices (Happy Paths) como los escenarios de error (Sad Paths), desde una perspectiva de negocio.

### 5.1 Registro de Usuario (Traditional Sign-Up)
**Actor:** Nuevo Usuario
**Precondición:** No tiene cuenta registrada.

| Escenario | Entrada | Resultado Esperado | Código HTTP |
|-----------|---------|--------------------|-------------|
| **✅ Registro Exitoso** | Email válido, Password segura (>8 chars), Username (opcional) | Cuenta creada, sesión iniciada (Tokens retornados) | 200 OK |
| **❌ Email Duplicado** | Email ya registrado en el sistema | Error indicando que el correo ya existe | 409 Conflict |
| **❌ Datos Inválidos** | Email malformado o Password corta | Error de validación con detalles | 400 Bad Request |

### 5.2 Inicio de Sesión (Login)
**Actor:** Usuario Existente
**Precondición:** Tiene cuenta registrada con contraseña.

| Escenario | Entrada | Resultado Esperado | Código HTTP |
|-----------|---------|--------------------|-------------|
| **✅ Login Exitoso** | Email y Password correctos | Sesión iniciada (Access Token + Refresh Cookie) | 200 OK |
| **❌ Credenciales Inválidas** | Email no registrado o Password incorrecta | Error genérico de credenciales (seguridad) | 401 Unauthorized |
| **❌ Faltan Datos** | Email o Password vacíos | Error de validación | 400 Bad Request |

### 5.3 Login con Google (Social Auth)
**Actor:** Usuario con cuenta Google
**Precondición:** Tiene token válido de Google.

| Escenario | Condición del Usuario | Resultado Esperado | Código HTTP |
|-----------|-----------------------|--------------------|-------------|
| **✅ Nuevo Usuario** | Email de Google NO existe en DB | Crea cuenta nueva (con GoogleID), inicia sesión | 200 OK |
| **✅ Usuario Existente (Vinculación)** | Email existe (creado por password) pero no tiene GoogleID | Vincula la cuenta existente con Google, inicia sesión | 200 OK |
| **✅ Usuario Recurrente** | Email existe y ya tiene GoogleID vinculado | Inicia sesión correctamente | 200 OK |
| **❌ Token Inválido** | Token de Google expirado o falso | Rechaza el acceso | 401 Unauthorized |

### 5.4 Renovación de Sesión (Token Refresh)
**Actor:** Usuario con sesión expirada (pero "Recordarme" activo implícito)
**Precondición:** Cookie `refresh_token` presente en el navegador.

| Escenario | Condición del Token | Resultado Esperado | Código HTTP |
|-----------|---------------------|--------------------|-------------|
| **✅ Renovación Exitosa** | Token válido y no expirado | Nuevo Access Token, Cookie rotada (nuevo refresh token) | 200 OK |
| **❌ Token Expirado** | Token venció hace más de 7 días | Sesión finalizada, requiere login manual | 401 Unauthorized |
| **⚠️ Robo de Token (Reuse)** | Token ya fue usado anteriormente | **ALERTA SEGURIDAD:** Revoca TODAS las sesiones del usuario | 401 Unauthorized |
| **❌ Sin Cookie** | No se envía cookie | Rechaza renovación | 401 Unauthorized |

### 5.5 Cierre de Sesión (Logout)
**Actor:** Usuario Autenticado

| Escenario | Acción | Resultado Esperado | Código HTTP |
|-----------|--------|--------------------|-------------|
| **✅ Logout Exitoso** | Usuario solicita salir | Elimina cookie `refresh_token`, cierra sesión local | 200 OK |

## 6. Riesgos y Dependencias

* **Dependencias:** 
  - Google Cloud Console configurado con OAuth 2.0 credentials
  - Variables de entorno: `JWT_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - Turso database con tabla `users`

* **Riesgos:** 
  - Exposición de JWT_SECRET_KEY comprometería todos los tokens
  - Google OAuth mal configurado bloqueará login social
  - Migración de usuarios existentes si hay datos previos

## 6. Decisiones de Diseño (Resolución de Ambigüedades)

### 6.1 Email en Google OAuth
**Decisión:** NO validar formato de email, solo verificar que existe en el token de Google.
**Razón:** 
- 🔒 **Seguridad:** Google ya valida y verifica emails antes de emitir el token
- 👤 **UX:** Confiamos en la verificación de Google, reduciendo fricción
- **Implementación:** Aceptar email tal cual viene en el Google ID token

### 6.2 Conflicto de Cuentas (Username vs Google Email)
**Decisión:** Usar EMAIL como identificador único. Si existe una cuenta con username y luego el usuario hace login con Google usando el mismo email, hacer MERGE de cuentas.

**Razón:**
- 🔒 **Seguridad:** Un email = una persona. Evita suplantación de identidad
- 👤 **UX:** El usuario no queda bloqueado de su cuenta si olvida cómo se registró
- **Comportamiento:**
  1. Usuario se registra con username "juan123" y email opcional vacío
  2. Usuario posteriormente hace login con Google (email: juan@gmail.com)
  3. Sistema pregunta: "¿Ya tienes una cuenta? Vincúlala con Google"
  
**Flujo de implementación:**
- Si Google login y email existe → vincular GoogleID a cuenta existente
- Si Google login y email NO existe → crear nueva cuenta con GoogleID
- **REGLA IMPORTANTE:** Username es opcional para cuentas de Google (puede auto-generarse del email)

### 6.3 Almacenar Refresh Token de Google
**Decisión:** NO almacenar refresh tokens de Google en esta iteración.

**Razón:**
- 🔒 **Seguridad:** Menos superficie de ataque. No almacenamos credenciales de terceros
- 👤 **UX:** Para esta versión solo necesitamos verificar identidad una vez
- **Alcance:** Solo verificamos el Google ID token para crear/login, luego usamos nuestro propio JWT
- **Futuro:** Si necesitamos acceder a APIs de Google (Gmail, Calendar), reconsiderar en otra iteración

### 6.4 Estructura Final de User Model
```go
type User struct {
    ID           string    // UUID generado por nosotros
    Username     string    // Requerido para auth tradicional, opcional para Google
    Email        *string   // ÚNICO - identificador principal
    PasswordHash *string   // NULL si es cuenta de Google
    GoogleID     *string   // NULL si es auth tradicional
    CreatedAt    time.Time 
    UpdatedAt    time.Time 
}
```

**Restricciones de unicidad:**
- Email debe ser UNIQUE (índice en DB)
- GoogleID debe ser UNIQUE cuando no es NULL
- Username debe ser UNIQUE cuando no es NULL
