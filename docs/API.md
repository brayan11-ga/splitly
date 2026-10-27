# API REST — FastAPI

Raíz `/api`; JSON. FastAPI genera documentación interactiva en `/docs` (OpenAPI).

| Método | Ruta | Acción |
|---|---|---|
| GET | `/api/health` | Estado de API (implementado) |
| GET/POST | `/api/groups` | Listar/crear grupos (implementado) |
| GET/PATCH/DELETE | `/api/groups/{group_id}` | Detalle/editar/borrar grupo (implementado) |
| GET/POST | `/api/groups/{group_id}/members` | Listar/agregar miembros (implementado) |
| PATCH/DELETE | `/api/groups/{group_id}/members/{member_id}` | Editar/eliminar miembro del grupo (implementado) |
| GET/POST | `/api/groups/{group_id}/expenses` | Listar/crear gastos (pendiente) |
| PATCH/DELETE | `/api/expenses/{expense_id}` | Editar/eliminar gasto (pendiente) |
| GET | `/api/groups/{group_id}/balances` | Saldos y transferencias (pendiente) |

El endpoint de salud devuelve HTTP 200 con `{"status":"ok"}` sin consultar PostgreSQL; no es una comprobación de disponibilidad de la base de datos. Swagger está en `/docs` y el esquema en `/openapi.json`. Grupos y participantes utilizan persistencia PostgreSQL.

## Contrato de grupos y participantes

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
3. Crear un grupo con POST y copiar el `id`; consultar la lista y el detalle.
4. Usar ese ID para crear/listar participantes; copiar el ID del participante para PATCH y DELETE anidados.
5. Probar un nombre vacío (422), un UUID válido inexistente (404) y borrar un grupo con participantes (409). Para eliminarlo, borrar primero los participantes y repetir DELETE (204).

Swagger usa la base configurada del servidor: probar únicamente con datos ficticios que se puedan modificar o eliminar.

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
