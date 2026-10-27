# API REST propuesta — FastAPI

Raíz `/api`; JSON. FastAPI genera documentación interactiva en `/docs` (OpenAPI).

| Método | Ruta | Acción |
|---|---|---|
| GET | `/api/health` | Estado de API (implementado) |
| GET/POST | `/api/groups` | Listar/crear grupos |
| GET/PATCH/DELETE | `/api/groups/{group_id}` | Detalle/editar/borrar grupo |
| GET/POST | `/api/groups/{group_id}/members` | Listar/agregar miembros |
| PATCH/DELETE | `/api/members/{member_id}` | Editar/eliminar miembro |
| GET/POST | `/api/groups/{group_id}/expenses` | Listar/crear gastos |
| PATCH/DELETE | `/api/expenses/{expense_id}` | Editar/eliminar gasto |
| GET | `/api/groups/{group_id}/balances` | Saldos y transferencias |

Solo el endpoint de salud está implementado. Devuelve HTTP 200 con `{"status":"ok"}` sin consultar PostgreSQL; no es una comprobación de disponibilidad de la base de datos. Swagger está en `/docs` y el esquema en `/openapi.json`. Las demás rutas siguen propuestas.

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
