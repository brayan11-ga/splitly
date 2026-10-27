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
| GET/POST | `/api/groups/{group_id}/expenses` | Listar/crear gastos |
| GET/PATCH/DELETE | `/api/groups/{group_id}/expenses/{expense_id}` | Consultar/editar/eliminar gasto |
| GET | `/api/groups/{group_id}/balances` | Saldos y transferencias sugeridas |

El endpoint de salud devuelve HTTP 200 con `{"status":"ok"}` sin consultar PostgreSQL; no es una comprobación de disponibilidad de la base de datos. Swagger está en `/docs` y el esquema en `/openapi.json`. Grupos y participantes utilizan persistencia PostgreSQL.

## Contrato de grupos y participantes

Todas estas rutas requieren una sesión válida (401 si falta, está revocada o expirada). Las consultas y escrituras se limitan al propietario autenticado: grupos ajenos o previos sin propietario devuelven 404 y no aparecen en listas. owner_id se asigna en el servidor y enviarlo en un payload devuelve 422. Los gastos y balances reutilizan `get_current_user` y verifican el propietario con `services.groups.get_group` antes de operar.

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

## Gastos y balances implementados

**Unidad: pesos colombianos enteros**, no centavos. Este contrato reemplaza la propuesta anterior amount_cents/paid_by_member_id por amount/paid_by. No existían tablas ni API de gastos implementadas que convertir. No se admiten floats, booleanos, cadenas numéricas, cantidades <= 0 ni mayores que 9007199254740991. La suma de importes de un grupo también se limita por la API a ese máximo, para mantener precisión en JSON/JavaScript.

Ejemplo `POST /api/groups/{group_id}/expenses`:

```json
{
  "description": "Cena",
  "amount": 90000,
  "paid_by": "UUID_ANA",
  "participant_ids": ["UUID_ANA", "UUID_PEDRO", "UUID_LAURA"]
}
```

Los marcadores UUID deben sustituirse por IDs reales de miembros del mismo grupo. Description: texto estricto, recortado, 1–240 caracteres. Lista de 1–1000 UUID únicos; pagador y participantes del mismo grupo. El pagador puede no participar del consumo. No se aceptan campos extra (id, owner_id, group_id, shares, etc.).

POST devuelve 201 y ExpenseRead: `id`, `group_id`, `paid_by`, `description`, `amount`, `created_at` UTC y `shares: [{member_id, amount_owed}]`. Las partes se ordenan por UUID ascendente. La suma de amount_owed coincide exactamente con amount. Una parte puede ser 0 si hay más participantes que pesos; el gasto total debe ser positivo.

- GET colección: 200, lista ordenada por created_at/id; grupo sin gastos devuelve `[]`.
- GET detalle: 200, mismo formato que POST; buscar un gasto bajo otro grupo devuelve 404.
- PATCH detalle: 200; admite uno o varios campos de creación. Los omitidos se conservan, null y cuerpo vacío se rechazan con 422. Reemplaza el reparto completo de forma atómica y no cambia id/group_id/created_at. Una modificación de amount o participant_ids siempre recalcula shares.
- DELETE detalle: 204 sin cuerpo, elimina deliberadamente el gasto y sus partes; recalcular balances no registra pagos.
- Todas las rutas requieren sesión (401), pertenencia por propietario (404 para grupo inexistente/ajeno) y CSRF para escrituras (403 si falta/es incorrecto el token u Origin).
- 422 para payload inválido, participante inexistente/ajeno al grupo o límite de importe. 409 para conflictos de integridad concurrentes; rollback de gasto y reparto completo. Errores SQL inesperados devuelven 500 genérico.
- Eliminar un participante pagador o beneficiario de cualquier gasto devuelve 409, incluso si su parte es 0. Primero editar/eliminar los gastos asociados. Las FKs impiden saltarse esta política por SQL. Renombrarlo está permitido y no cambia sus IDs ni importes.

### Balances

`GET /api/groups/{group_id}/balances` devuelve 200:

```json
{
  "group_id": "UUID_GRUPO",
  "total_amount": 90000,
  "expense_count": 1,
  "members": [
    {"member_id": "UUID_ANA", "name": "Ana", "total_paid": 90000, "total_owed": 30000, "net_balance": 60000},
    {"member_id": "UUID_PEDRO", "name": "Pedro", "total_paid": 0, "total_owed": 30000, "net_balance": -30000},
    {"member_id": "UUID_LAURA", "name": "Laura", "total_paid": 0, "total_owed": 30000, "net_balance": -30000}
  ],
  "transfers": [
    {"from_member_id": "UUID_PEDRO", "to_member_id": "UUID_ANA", "amount": 30000},
    {"from_member_id": "UUID_LAURA", "to_member_id": "UUID_ANA", "amount": 30000}
  ]
}
```

El orden de transfers del ejemplo es ilustrativo: el real se determina por UUID ascendente de deudores/acreedores, no por nombre ni orden de alta. Miembros se muestran en orden estable de creación/ID. Se incluyen miembros sin movimientos con ceros. Grupo vacío devuelve total 0, expense_count 0 y listas vacías.

Balance neto = total_paid − total_owed. Positivo recibe, negativo paga. La suma siempre es cero. Para importes no divisibles se usa divmod y los primeros UUID ascendentes reciben +1 peso. La liquidación empareja deudores y acreedores ordenados; consume el menor saldo pendiente en cada paso. Es determinista, sin garantía de mínimo global de transferencias y sin pagos bancarios ni registro de liquidaciones.

Las respuestas conservan Cache-Control:no-store y viajan por el proxy Pages existente con VITE_API_URL vacío. Swagger en /docs publica estos modelos/endpoints y reutiliza el flujo de cookie/Origin/CSRF anterior.
