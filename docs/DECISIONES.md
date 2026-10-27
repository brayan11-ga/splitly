# Registro de decisiones (ADR sencillo)

## 2026-10-27 — Arquitectura full-stack
- Frontend: React + Vite + Tailwind CSS porque la aplicación es interactiva.
- Backend: Python + FastAPI (sustituye la propuesta inicial de Express) por preferencia del equipo y validación/documentación OpenAPI integrada.
- ORM: SQLModel; base de datos PostgreSQL en Supabase; evita persistencia temporal del navegador.
- UI: Motion y React Bits primero; Three.js + React Three Fiber solo como mejora si el MVP está completo, priorizando accesibilidad y performance.
- Moneda COP almacenada como centavos enteros según contrato técnico; la UI muestra valores formateados.
- Sin login en el MVP: no usar información sensible real.

Actualizar cuando se implemente o cambie alguna decisión.

## 2026-10-27 — Esqueleto funcional del backend
- Salud en `GET /api/health`, alineada con la raíz `/api` solicitada. Es una comprobación de respuesta HTTP, independiente de PostgreSQL.
- Configuración con Pydantic y python-dotenv desde `server/.env`, con precedencia del entorno del proceso; secretos mediante `SecretStr`.
- SQLModel con driver psycopg 3 y `pool_pre_ping`; motor diferido y sesiones por petición, sin crear tablas automáticamente ni persistencia en memoria.
- CORS explícito para los dos orígenes locales Vite; variable `CORS_ORIGINS` separada por comas. Revisar orígenes de producción antes de desplegar.
- Dependencias fijadas a las versiones del entorno existente. pytest y httpx permiten verificar salud, OpenAPI y CORS sin credenciales ni PostgreSQL.
- Modelos, servicios, migraciones y pruebas de cálculo quedan pendientes de las iteraciones de CRUD y reparto; esta iteración no implementa cálculos.

## 2026-10-27 — PostgreSQL local y Supabase con Alembic
- Desarrollo en PostgreSQL Windows (`splitly_dev`), producción en Supabase, seleccionados únicamente con `DATABASE_URL`. No se incluyen credenciales reales ni se crea una base automáticamente.
- Se reutilizan motor y dependencia de sesiones; se centraliza la validación de URLs PostgreSQL y se limita la espera de conexión. Cada servicio gestionará sus transacciones explícitamente.
- Alembic 1.20.1 con metadata SQLModel y revisión inicial aditiva Group/Member. UUID en aplicación, fechas con zona horaria y default SQL, FK e índice de pertenencia, sin cascada de borrado. No se ejecuta ninguna migración en esta iteración.
- Downgrade inicial bloqueado por implicar borrado de tablas. Migraciones futuras requieren revisión manual; se omiten tablas externas en propuestas de borrado de autogenerate.
- Comprobación local separada del health HTTP: lectura `SELECT 1`, solo base `splitly_dev` en loopback, errores sin credenciales. Supabase queda documentado para una ejecución posterior autorizada.
- Se verificaron diez pruebas (salud, CORS, sesiones, URLs, protección de credenciales y equivalencia DDL modelo/migración), cabecera Alembic y dependencias. La conexión real no se verificó: falta DATABASE_URL/server/.env, aunque el servicio PostgreSQL de Windows aparece activo.
