# Splitly — Gastos compartidos

Prototipo web para crear grupos, registrar gastos y calcular deudas simplificadas. **Estado: backend con CRUD de grupos y participantes**, salud, CORS y PostgreSQL. Gastos y balances siguen pendientes.

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
4. Si no existe `server/.env`, crearlo con las variables del servidor indicadas en `.env.example` de la raíz (DATABASE_URL y CORS_ORIGINS). Sustituir `DATABASE_URL` por una conexión PostgreSQL propia antes de usar persistencia. Las variables del sistema prevalecen sobre `.env`. `CORS_ORIGINS` es una lista separada por comas; permite por defecto `http://localhost:5173` y `http://127.0.0.1:5173`. Definir `VITE_API_URL` solo en `client/.env`; nunca copiar credenciales al cliente.
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

Para cambios posteriores: `python -m alembic revision --autogenerate -m "descripcion"`, revisar el archivo generado y su SQL antes de aplicarlo. El CRUD actual no requiere migraciones nuevas. El downgrade inicial está bloqueado para evitar borrar datos accidentalmente.

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
Sin autenticación/autorización en este prototipo; usar exclusivamente datos ficticios. No subir secretos. Las demostraciones no equivalen a una app de finanzas segura en producción.
