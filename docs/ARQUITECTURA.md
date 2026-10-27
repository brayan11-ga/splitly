# Arquitectura técnica propuesta

## Capas
- `client/src/pages/`: grupos, detalle, nuevo gasto, balances.
- `client/src/components/`: UI reutilizable, gráficas, efectos visuales accesibles.
- `client/src/services/api.js`: peticiones a FastAPI y manejo de errores.
- `server/app/main.py`: aplicación FastAPI, CORS explícito para origen frontend.
- `server/app/routers/`: endpoints REST.
- `server/app/models/`: tablas SQLModel; `schemas/`: payloads y respuestas.
- `server/app/services/`: operaciones de negocio y cálculo de balances.
- `server/app/db/`: conexión PostgreSQL y sesiones.
- `server/tests/`: pruebas pytest (incluida lógica de dinero).

## Modelo de datos
El backend implementa `main.py`, configuración en `config.py`, router y esquema de salud, conexión/sesiones en `db/session.py` y modelos `Group`/`Member`. `services/` está reservado para el CRUD y los cálculos. La conexión a PostgreSQL es diferida y el endpoint de salud funciona sin `DATABASE_URL`.

- `groups`: id UUID, name, created_at.
- `members`: id UUID, group_id FK, name, created_at.
- `expenses`: id UUID, group_id FK, paid_by_member_id FK, description, amount_cents BIGINT, created_at.
- `expense_shares`: id UUID, expense_id FK, member_id FK, amount_cents BIGINT.
- Índices en claves foráneas y pertenencia; validar que todos sean del mismo grupo.

## Matemática
Saldo(miembro) = total pagado - total de participaciones asignadas. Positivo: recibe; negativo: paga.
Reparto igualitario de enteros: `q, r = divmod(amount_cents, n)`; cada uno recibe q; los primeros r miembros según orden determinista reciben +1 centavo. La suma de participaciones debe coincidir exactamente con el gasto.
Liquidación: emparejar saldo negativo y positivo, generar transferencias de mínimo monto, actualizar saldos hasta cero. Asegurar suma total de saldos = 0.

## Diseño y UX
Stitch para wireframes verificables. React Bits/Motion para fondos, microinteracciones y cambios de estado; Recharts para reportes. React Three Fiber / Three.js solo para una escena opcional con lazy loading; fallback estático. Evitar 3D en formularios y tablas. Reducir animación si `prefers-reduced-motion`.

## Infraestructura
Supabase PostgreSQL (credenciales solamente en backend), FastAPI en Render, cliente Vite en Vercel. CORS debe permitir solo orígenes esperados. Verificar proveedores y cuotas al desplegar.

## Entornos y ciclo de esquema
- Desarrollo: PostgreSQL local Windows, base `splitly_dev`; producción: PostgreSQL Supabase. Ambos usan SQLModel, psycopg 3 y `DATABASE_URL`, sin alternativa SQLite.
- `server/.env` solo para desarrollo; las variables del proceso prevalecen. En producción se inyectan secretos en el backend. TLS en la conexión de producción y CORS explícito del cliente desplegado.
- `get_session` es una dependencia generadora reutilizable mediante `Depends(get_session)`: abre una sesión por petición y la cierra al finalizar. Las operaciones de negocio deberán decidir `commit`/`rollback`; no hay commit automático. Motor con `pool_pre_ping`, timeout de conexión de 5 segundos y parámetros SQL ocultos.
- Alembic lee la misma configuración, importa `app.models` y usa `SQLModel.metadata`. No se ejecuta `create_all` ni migraciones al iniciar FastAPI. `alembic.ini` no contiene URL ni credenciales.
- Revisión `0001_groups_members`: UUID generados en Python, nombres no nulos y fechas UTC con `TIMESTAMP WITH TIME ZONE` y valor por defecto SQL. FK `members.group_id -> groups.id` sin borrado en cascada e índice `ix_members_group_id`. Tablas de gastos pendientes.
- La autogeneración omite propuestas de borrado de tablas reflejadas ajenas al metadata. Esto no sustituye revisar cada migración: no elimina columnas ni tablas automáticamente de forma segura. El downgrade inicial está bloqueado expresamente.
- `python -m app.db.check` comprueba solo PostgreSQL local `splitly_dev` con `SELECT 1`, sin mostrar URL ni mensajes del driver. Ver instrucciones de aplicación local y futura aplicación en Supabase en README.
