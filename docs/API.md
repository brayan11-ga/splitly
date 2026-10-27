# API REST — FastAPI

Raíz `/api`; JSON. FastAPI genera documentación interactiva en `/docs` (OpenAPI).

| Método | Ruta | Acción |
|---|---|---|
| GET | `/api/health` | Estado de API (implementado) |
| POST | `/api/auth/register` | Crear usuario y sesión, 201 |
| POST | `/api/auth/login` | Iniciar sesión, 200 |
| POST | `/api/auth/logout` | Revocar sesión actual y borrar cookie, 204 |
| GET | `/api/auth/me` | Usuario y CSRF de la sesión actual, 200 |
| GET/POST | `/api/groups` | Listar/crear grupos (implementado) |
| GET/PATCH/DELETE | `/api/groups/{group_id}` | Detalle/editar/borrar grupo (implementado) |
| GET/POST | `/api/groups/{group_id}/members` | Listar/agregar miembros (implementado) |
| PATCH/DELETE | `/api/groups/{group_id}/members/{member_id}` | Editar/eliminar miembro del grupo (implementado) |
| GET/POST | `/api/groups/{group_id}/expenses` | Listar/crear gastos (pendiente) |
| PATCH/DELETE | `/api/expenses/{expense_id}` | Editar/eliminar gasto (pendiente) |
| GET | `/api/groups/{group_id}/balances` | Saldos y transferencias (pendiente) |

El endpoint de salud devuelve HTTP 200 con `{"status":"ok"}` sin consultar PostgreSQL; no es una comprobación de disponibilidad de la base de datos. Swagger está en `/docs` y el esquema en `/openapi.json`. Grupos y participantes utilizan persistencia PostgreSQL.

## Contrato de grupos y participantes

Todas estas rutas requieren una sesión válida (401 si falta, está revocada o expirada). Las consultas y escrituras se limitan al propietario autenticado: grupos ajenos o previos sin propietario devuelven 404 y no aparecen en listas. owner_id se asigna en el servidor y enviarlo en un payload devuelve 422. Los futuros gastos deben exigir `get_current_user` y pasar el usuario a `services.groups.get_group` antes de operar.

Los POST y PATCH reciben `{"name":"Viaje"}` para grupos o `{"name":"Ana"}` para participantes. `name` es obligatorio, debe ser texto y se recortan espacios al inicio y al final. Nombres vacíos o solo espacios, null, números, cuerpo vacío y campos adicionales devuelven 422. PATCH requiere `name` porque es el único campo editable; no permite modificar IDs, pertenencia ni fechas. Los nombres duplicados están permitidos: no hay restricción de unicidad en el esquema actual.

| Operación | Éxito |
|---|---|
| POST de grupo/participante | 201 con el registro creado |
| GET de listas | 200 con array; `[]` si no hay registros |
| GET de grupo | 200 con el registro |
| PATCH de grupo/participante | 200 con el registro actualizado |
| DELETE de grupo/participante | 204 sin cuerpo |

Grupo: `{"id":"UUID","name":"Viaje","created_at":"FECHA_ISO_8601"}`. Participante: los mismos campos más `"group_id":"UUID"`. Las listas se ordenan por fecha de creación e ID para un orden estable; no hay paginación en esta iteración.

Errores con `detail`: 404 para grupo o participante inexistente, incluyendo participantes que pertenecen a otro grupo; 422 para UUID inválidos o solicitudes inválidas. El GET de participantes exige un grupo existente. No se implementan rutas de participantes fuera del grupo.

Eliminar un grupo con participantes devuelve **409**, conservando todos sus datos; primero hay que eliminar explícitamente los participantes. La FK sin cascada protege también contra referencias concurrentes. Otros conflictos de integridad devuelven 409 y revierten la transacción; fallos SQL inesperados devuelven 500 con mensaje genérico, sin SQL ni credenciales. Cada escritura confirma su transacción. Las operaciones futuras de gastos deberán conservar esta protección de referencias.

## Probar en Swagger

1. Desde `server/`, iniciar `python -m uvicorn app.main:app --reload` con DATABASE_URL local configurada y la migración existente aplicada.
2. Abrir `http://127.0.0.1:8000/docs`, desplegar una operación y seleccionar **Try it out**.
3. Registrar o iniciar sesión mediante `/api/auth/register` o `/api/auth/login`: en el campo de cabecera `x-csrf-token` escribir `bootstrap`. Swagger debe servirse desde un origen permitido (en producción añadir la URL API a CSRF_TRUSTED_ORIGINS). El navegador conserva la cookie HttpOnly automáticamente.
4. Copiar `csrf_token` de la respuesta o de `/api/auth/me` en el campo de cabecera `x-csrf-token` de cada POST/PATCH/DELETE autenticado, incluido logout. Crear un grupo, copiar su `id` y consultar lista/detalle.
5. Usar ese ID para crear/listar participantes; copiar el ID del participante para PATCH y DELETE anidados.
6. Probar un nombre vacío (422), un UUID válido inexistente o ajeno (404) y borrar un grupo con participantes (409). Para eliminarlo, borrar primero los participantes y repetir DELETE (204).

Swagger usa la base configurada del servidor: probar únicamente con datos ficticios que se puedan modificar o eliminar.

## Autenticación y CSRF

Registro: `{"full_name":"Persona Demo","email":"demo@example.com","password":"Una frase ficticia muy larga 123"}`. Login: `{"email":"demo@example.com","password":"Una frase ficticia muy larga 123"}`. Nombre recortado no vacío (máximo 120), email válido y normalizado a minúsculas sin espacios exteriores y restricción UNIQUE en PostgreSQL. Contraseña de registro entre 15 y 128 caracteres, sin recortarla; se protege con Argon2id/pwdlib. No se devuelve hashed_password. No se aceptan campos adicionales.

Registro, login y me devuelven `{"user":{"id":"UUID","full_name":"Persona Demo","email":"demo@example.com","created_at":"FECHA_ISO_8601"},"csrf_token":"TOKEN_CSRF"}`. El identificador de sesión solo se envía en Set-Cookie HttpOnly (Secure en producción); no se devuelve como JSON. Cookie host-only con TTL absoluto configurable (8 horas por defecto), sin renovación silenciosa. Cada login/registro rota y revoca la sesión anterior de esa cookie; otros dispositivos conservan sus propias sesiones. Logout revoca la sesión actual en PostgreSQL; reutilizar la cookie devuelve 401. Si ya expiró, logout responde 401 y React elimina su estado local. Las respuestas API son no-store; los errores 422 omiten el valor input.

Para TODAS las escrituras se exige un Origin exacto permitido. Login/registro también requieren una cabecera no simple `X-CSRF-Token` (el cliente usa `bootstrap` antes de tener sesión), lo que obliga a preflight; no es una clave secreta. Las escrituras autenticadas exigen además el CSRF ligado a la sesión devuelto por me/login/registro, comparado en tiempo constante. React lo conserva solo en memoria y envía credentials:include; al recargar vuelve a consultar me. Origen ausente/null/ajeno o CSRF ausente/incorrecto con sesión válida devuelve 403. CORS permite credenciales solo para orígenes explícitos. No se usa SameSite como única defensa. Referencia: [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

401 para login inválido (mismo mensaje de correo inexistente o contraseña incorrecta) o sesión inválida; 403 para origen/CSRF; 409 para correo ya registrado, incluida concurrencia por UNIQUE; 422 para datos inválidos. El registro con 409 permite inferir que un correo no se pudo registrar, limitación conocida; no hay verificación de correo, recuperación ni limitador de intentos todavía. Antes de abrir al público, añadir límites persistentes en servidor/gateway.

## Gastos y balances (propuesta pendiente)

Ejemplo `POST /api/groups/{group_id}/expenses`:
```json
{
  "description": "Cena",
  "amount_cents": 9000000,
  "paid_by_member_id": "UUID_PAGADOR",
  "participant_ids": ["UUID_ANA", "UUID_PEDRO", "UUID_LAURA"]
}
```
`9000000` centavos equivalen a COP 90.000. Contrato propuesto, sujeto a pruebas y decisión sobre unidad monetaria. Usar 201 para creación, 422 para payload inválido, 404 para no encontrado, 409 para conflicto y 500 para fallo inesperado; traducir errores controlados sin filtrar secretos.
