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
El backend implementa `main.py`, configuración en `config.py`, salud y CRUD de grupos/participantes. `routers/` traduce HTTP, `schemas/` valida y serializa, `services/` aplica reglas y confirma transacciones, y `db/repositories.py` concentra consultas SQLModel sobre `Group`/`Member`. La conexión en `db/session.py` es diferida y el endpoint de salud funciona sin `DATABASE_URL`. Cálculos y gastos siguen pendientes.

- `groups`: id UUID, name, created_at.
- `users`: id UUID, full_name, email normalizado UNIQUE y CHECK, hashed_password Argon2id, created_at con zona horaria.
- `auth_sessions`: token_hash SHA-256 PK, user_id FK/indexado, expires_at con zona horaria/indexado, created_at. No almacena el token en claro.
- `groups.owner_id`: FK/index a users, nullable únicamente para conservar datos anteriores sin propietario; el servidor siempre asigna propietario al crear desde la API.
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

## Autenticación y autorización

### Gestión frontend de grupos y participantes

- `pages/GroupsPage.jsx` muestra la lista y `GroupDetailPage.jsx` carga grupo/miembros en paralelo, con clave React por groupId para aislar cada ruta. Las tres páginas privadas comparten WorkspaceNav y logout; todas usan ProtectedRoute.
- `components/workspace/GroupsPanel` comparte lista completa y vista previa del dashboard (tres grupos recientes); GroupCard muestra nombre y fecha reales. ResourceState gestiona loading/error/reintento/404. ActionDialog comparte formulario/confirmación HTML nativa con foco modal, Escape, restauración de foco, estados de envío/error y entrada Motion breve. Reduced motion elimina las entradas; estilos acotados a workspace.css.
- `services/groups.js` adapta solo los nueve endpoints documentados y envía exclusivamente name en POST/PATCH. Usa apiRequest, cookies y CSRF; no admite owner_id. `utils/format.js` formatea fechas. No se modifican modelos, backend ni migraciones.
- `useRemoteResource` cancela lecturas al desmontar e ignora resultados abortados. Cada página consulta de nuevo al entrar; las escrituras actualizan estado transitorio solo después del éxito REST. Eliminar espera 204 antes de retirar registros. Actualizar recarga cambios externos. No hay persistencia local ni caché compartida entre usuarios.
- Búsqueda local por nombre sin acentos/mayúsculas. 409 al eliminar grupo conserva datos y enlaza a gestionar participantes. 401 redirige al login con explicación; 403 conserva formulario y pide recargar; 404 no muestra gestión; 422 distingue nombre inválido de UUID inválido. Gastos y balances se señalan como pendientes.
- Playwright recorre CRUD, navegación, autorización y persistencia contra API/PostgreSQL temporal reales. Para 403/422 se altera la petición de prueba y la respuesta procede del servidor real; solo el error de red se induce abortando peticiones. Capturas de escritorio y 390 px ignoradas por Git; no se toca splitly_dev.

### Sesiones y seguridad

La solicitud de autenticación reemplaza la decisión inicial de MVP anónimo. `schemas/auth.py` valida entradas y publica solo UserRead; `services/auth.py` gestiona Argon2, tokens opacos aleatorios de 256 bits, rotación, expiración absoluta y revocación; `db/auth_repository.py` concentra consultas. Cookie HttpOnly host-only, Secure obligatorio en producción, SameSite configurable. No hay JWT ni clave de firma global; no existe una clave predeterminada de producción. README documenta generación criptográfica si otra integración futura necesita una clave independiente.

`get_current_user` consulta la sesión PostgreSQL y rechaza tokens inexistentes o expirados antes de autorizar. Cada operación de grupos recibe el usuario autenticado; las consultas filtran owner_id. Todas las operaciones de participantes pasan primero por `services.groups.get_group(session, group_id, owner_id)`. El mismo punto de autorización debe preceder futuras operaciones de gastos, sin aceptar propietario del cliente. Grupo ajeno y grupo no existente devuelven el mismo 404. Un propietario sigue sin poder borrar un grupo con participantes (409).

CSRF combina validación estricta del Origin y cabecera personalizada antes del login/registro; después exige además un token HMAC derivado del identificador aleatorio de sesión, devuelto en JSON y comparado en tiempo constante. Nunca se acepta el CSRF como autenticación. CORS explícito con credenciales; me y demás respuestas API no-store. Los errores de validación eliminan input y los fallos SQL usan mensajes genéricos, sin logs de contraseñas, SQL ni cookies.

React separa `services/api.js`, `services/auth.js`, `auth/AuthProvider` y `ProtectedRoute`, páginas de formularios y dashboard. El servicio usa credentials:include y CSRF en memoria; /me restaura usuario/CSRF tras recargar, y los 401 de operaciones privadas invalidan el estado React. Errores de red no se confunden con una sesión anónima en el arranque: muestran una opción de reintento. Dashboard, /groups y /groups/:groupId implementan la gestión visual completa de grupos/participantes. Gastos pendientes. Los componentes, estilos e interacciones existentes de la Landing se preservan.

La revisión aditiva `0002_auth_ownership` conserva los grupos y participantes de 0001 con owner_id NULL e inaccesibles desde la API; su asignación solo puede hacerse manualmente después de verificar titularidad. No se ejecutó ninguna migración ni actualización de datos en splitly_dev o producción. Los tests migran datos previos únicamente en una base local temporal exclusiva; Alembic check verifica equivalencia de esquema. Playwright usa otra API de pruebas y una base temporal real, con cierre cooperativo para retirarla en Windows.

Producción requiere TLS, orígenes definitivos, configuración de cookies y dominio coherente, backups, limitación de intentos de autenticación y gestión operativa de sesiones expiradas. Preferir mismo sitio o proxy /api para evitar bloqueo de cookies de terceros. No se incorporan proveedores externos, MFA, recuperación de contraseña ni verificación de correo en esta iteración.
