# Splitly — Gastos compartidos

Prototipo web para crear grupos, registrar gastos y calcular deudas simplificadas. **Estado: autenticación React/FastAPI con sesiones PostgreSQL y CRUD privado de grupos y participantes**. Gastos y balances siguen pendientes.

## Stack
- Cliente: React, Vite, Tailwind CSS, React Router, Motion, React Bits; Recharts para gráficas; Three.js + React Three Fiber solo de manera progresiva.
- API: Python 3.11+, FastAPI, Pydantic, SQLModel, Uvicorn, pytest.
- Datos: PostgreSQL local (`splitly_dev`) en desarrollo; PostgreSQL Supabase en producción. Migraciones con Alembic.
- Despliegue previsto: Vercel (cliente), Render (API).

## MVP
CRUD de grupos, participantes y gastos; reparto igualitario entre participantes seleccionados; balance por miembro y sugerencias de pagos; validaciones y persistencia real.

## Arquitectura
`client/ (React) -> HTTP JSON -> server/ (FastAPI) -> SQLModel -> PostgreSQL (Supabase)`.

## Desarrollo local
1. Instalar Node.js, Python 3.11+ y Git.
2. `cd client && npm install && npm run dev`.
3. En otra terminal: entrar a `server/`, ejecutar `python -m venv .venv` y activar el entorno (`.\.venv\Scripts\Activate.ps1` en PowerShell). Instalar con `python -m pip install -r requirements.txt`.
4. Si no existe `server/.env`, copiar `server/.env.example` y configurar la conexión propia. No sobrescribir un `.env` existente. Las variables del sistema prevalecen sobre `.env`. Consultar la tabla de configuración de autenticación más abajo. En `client/.env`, usar `VITE_API_URL=` vacío para el proxy local de Vite (ejemplo en `client/.env.example`); nunca copiar credenciales al cliente.
5. Lanzar la API: `python -m uvicorn app.main:app --reload`, desde `server/`; revisar `http://127.0.0.1:8000/docs`.
6. Consultar `http://127.0.0.1:8000/api/health`: devuelve `{"status":"ok"}`. No requiere conexión a PostgreSQL y no verifica su disponibilidad.
7. Desde `server/`, ejecutar `python -m pytest`.

La conexión usa SQLModel y psycopg 3, con sesiones por petición y transacciones explícitas en el CRUD. No se crean tablas ni se aplican migraciones al iniciar. Antes del despliegue se deben configurar los orígenes CORS exactos de producción. Consultar [el contrato y los pasos de Swagger](docs/API.md) para probar grupos y participantes.

## Base de datos y migraciones

En Windows, instala PostgreSQL y prepara la base local `splitly_dev` con un usuario propio mediante pgAdmin o las herramientas de PostgreSQL. Este proyecto no crea la base de datos. Configura en `server/.env` la URL del ejemplo con tus credenciales locales; codifica caracteres especiales del usuario/contraseña como componentes URL. No sobrescribas un `.env` existente al copiar el ejemplo.

Desde `server/`, con el entorno virtual activo:

```powershell
python -m app.db.check
python -m alembic heads
python -m alembic upgrade head --sql
# Aplicar solo después de verificar destino y revisar el SQL:
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

La comprobación ejecuta únicamente `SELECT 1`, acepta solo localhost/127.0.0.1/::1 y la base `splitly_dev`; devuelve código 1 si falta configuración o falla la conexión, sin imprimir credenciales. `upgrade head --sql` genera SQL sin conectarse a PostgreSQL ([documentación de Alembic](https://alembic.sqlalchemy.org/en/latest/offline.html)). La migración inicial crea `groups`, `members`, su FK y el índice de `group_id`. No reemplaza tablas existentes: si ya existen, detenerse y revisar el esquema; no borrar tablas ni marcar revisiones como aplicadas sin compararlas.

Para cambios posteriores: `python -m alembic revision --autogenerate -m "descripcion"`, revisar el archivo generado y su SQL antes de aplicarlo. La autenticación añade la revisión `0002_auth_ownership`; ver el procedimiento manual más abajo. Los downgrades están bloqueados para evitar borrar datos accidentalmente.

Producción en Supabase (procedimiento futuro, no ejecutado): obtener del panel la conexión PostgreSQL directa o la conexión de sesión apropiada para migraciones y accesible desde el entorno de despliegue. Guardar `DATABASE_URL` como secreto del backend con `postgresql+psycopg://` y TLS (`sslmode=require`); nunca en Vite ni en archivos versionados. Revisar respaldo, destino y SQL, luego ejecutar desde un entorno autorizado `python -m alembic current`, `python -m alembic upgrade head` y `python -m alembic check`. Utilizar la misma cadena de revisiones que en desarrollo. No generar migraciones contra los esquemas internos de Supabase ni usar el pool de transacciones para migrar. `app.db.check` rechaza intencionalmente este entorno.

## Pruebas de backend

Desde `server/`: `python -m pytest -p no:cacheprovider`. Las pruebas CRUD requieren PostgreSQL local y un usuario con permiso `CREATEDB` y acceso a la base administrativa `postgres`. Por defecto usan las credenciales de DATABASE_URL únicamente para crear una base temporal independiente `splitly_test_<UUID>`; nunca escriben en splitly_dev. Opcionalmente configura `TEST_DATABASE_URL` solo en `server/.env` o en el entorno del proceso para usar otro usuario local de pruebas. Se rechazan hosts remotos.

La ejecución aplica la migración existente en esa base temporal, prueba CRUD e integridad referencial y retira únicamente la base creada por ella al finalizar. Sin conexión o permisos, las pruebas de integración fallan con un mensaje genérico; no se sustituyen por SQLite ni se omiten silenciosamente. Si el proceso se interrumpe abruptamente, podría quedar una base temporal: revisar antes de retirarla manualmente.

## Documentación
- [Requisitos](docs/REQUISITOS.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Contrato API](docs/API.md)
- [Decisiones](docs/DECISIONES.md)
- [Registro de prompts](docs/PROMPTS.md)
- [Evidencias y pitch](docs/EVIDENCIAS.md)

## Evidencias / enlaces
- Capturas Google Stitch: pendiente
- Demo: pendiente
- GitHub: pendiente

## Seguridad y limitaciones
Hay autenticación y autorización por propietario; usar exclusivamente datos ficticios durante el hackathon. No subir secretos. Antes de habilitar uso público se requieren límites de intentos en login/registro, recuperación y verificación de correo, monitorización sin datos sensibles, HTTPS, respaldos y revisión del despliegue. No se afirma una auditoría de seguridad de producción.

## Landing pública (2026-10-27)

El cliente conserva la landing pública editorial y sus efectos Motion. `/login` y `/register` son formularios funcionales y `/dashboard` es privado, con listado de grupos propios y cierre de sesión. El ejemplo financiero de la landing sigue siendo ficticio. Detalles en [client/README.md](client/README.md).

## Autenticación: configurar y ejecutar

No hay JWT, localStorage ni clave de firma global. Cada sesión usa `secrets.token_urlsafe(32)` (256 bits aleatorios), y PostgreSQL almacena solo SHA-256 del token; logout borra la sesión. No configurar una SECRET_KEY ficticia: este diseño no la necesita. Si una integración futura requiere una clave aleatoria independiente, generar una vez con `python -c "import secrets; print(secrets.token_urlsafe(32))"` y guardarla en el gestor de secretos; nunca reutilizar ejemplos ni versionar su salida.

| Variable backend | Desarrollo | Producción |
|---|---|---|
| `DATABASE_URL` | PostgreSQL local splitly_dev | Secreto PostgreSQL con TLS |
| `ENVIRONMENT` | `development` | `production` |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Orígenes HTTPS exactos del cliente, separados por comas |
| `CSRF_TRUSTED_ORIGINS` | URLs API locales para Swagger, incluidas por defecto en desarrollo | URL pública HTTPS de la API si se usa Swagger; el cliente ya está permitido mediante CORS_ORIGINS |
| `COOKIE_SECURE` | `false`, HTTP local | `true`, obligatorio |
| `COOKIE_SAMESITE` | `lax` | `lax` en mismo sitio; `none` si son sitios distintos (requiere Secure) |
| `SESSION_TTL_SECONDS` | `28800` (8 horas) | Entre 60 y 86400 segundos; default 8 horas |

Orígenes sin rutas, barra final ni comodines. CORS usa credenciales. En producción la cookie es `__Host-splitly_session`, sin Domain y con Path=/; en desarrollo es `splitly_session`. Se rechazan configuraciones de producción inseguras. Es preferible frontend y API bajo el mismo sitio o un proxy `/api`: navegadores que bloquean cookies de terceros pueden impedir una sesión entre dominios Vercel/Render distintos incluso con SameSite=None. El proxy de Vite es solo de desarrollo; configurar el proxy de producción por separado o `VITE_API_URL=https://API_HOST` al compilar. No mezclar localhost y 127.0.0.1 cuando se use URL de API absoluta.

## Migración manual de autenticación

Esta tarea no aplica migraciones a splitly_dev ni a producción. Con respaldo revisado y desde `server/` con el entorno activo:

```powershell
python -m pip install -r requirements.txt
python -m alembic current
python -m alembic upgrade 0001_groups_members:head --sql
# Revisar el destino y el SQL antes de aplicar:
python -m alembic upgrade head
python -m alembic check
python -m uvicorn app.main:app --reload
```

La revisión `0002_auth_ownership` crea users y auth_sessions y añade owner_id nullable a groups con FK/índice. Conserva grupos y miembros previos; quedan sin propietario e invisibles para todos los usuarios. Ningún registro nuevo los reclama automáticamente. Para recuperarlos, un administrador debe verificar de forma independiente el usuario correcto y los grupos, y ejecutar una asignación explícita revisada en una transacción: `UPDATE groups SET owner_id = :usuario_verificado WHERE id = :grupo_verificado AND owner_id IS NULL`. Comprobar que se actualiza exactamente una fila antes de confirmar; no usar una actualización masiva ni asignar al primer usuario registrado. No se ejecutó este paso.

## Probar el flujo completo

Con la migración aplicada manualmente, iniciar API en 8000 y `npm run dev` desde client. Abrir `http://localhost:5173/register`, registrar nombre/correo ficticios y una frase de 15–128 caracteres. Debe llevar a `/dashboard`; recargar mantiene la sesión por `/api/auth/me`. Cerrar sesión lleva a login e invalida la cookie en el servidor; una visita directa a dashboard vuelve a login. Iniciar sesión con el mismo correo recupera únicamente los grupos propios. Ver [docs/API.md](docs/API.md) para Swagger y CSRF.

Backend: `python -m pytest -p no:cacheprovider` y `python -m pip check` desde server. Frontend: `npm run lint`, `npm run build` y `npm test` desde client. Playwright inicia React y FastAPI con PostgreSQL temporal real (puertos 5175/8001), prueba registro/login/recarga/logout y retira su base mediante cierre controlado; no usa la API de desarrollo. Requiere usuario PostgreSQL local con CREATEDB y navegador Edge en Windows; `PLAYWRIGHT_CHANNEL=chrome` permite Chrome instalado. En otros sistemas instalar Chromium con `npx playwright install chromium`. Si se mata el proceso abruptamente, revisar posibles bases temporales restantes antes de retirarlas. Los tests no muestran secretos ni guardan traces de red.
