# Splitly — Gastos compartidos

Prototipo web para crear grupos, registrar gastos y calcular deudas simplificadas. **Estado: autenticación React/FastAPI con sesiones PostgreSQL y CRUD privado de grupos y participantes**. Gastos y balances siguen pendientes.

## Stack
- Cliente: React, Vite, Tailwind CSS, React Router, Motion, React Bits; Recharts para gráficas; Three.js + React Three Fiber solo de manera progresiva.
- API: Python 3.11+, FastAPI, Pydantic, SQLModel, Uvicorn, pytest.
- Datos: PostgreSQL local (`splitly_dev`) en desarrollo; PostgreSQL Supabase en producción. Migraciones con Alembic.
- Despliegue: Cloudflare Pages (cliente y proxy `/api`), Render (API), Supabase (PostgreSQL).

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

El cliente conserva la landing pública editorial y sus efectos Motion. `/login` y `/register` son formularios funcionales; `/dashboard`, `/groups` y `/groups/:groupId` son privados. Incluyen grupos reales, gestión completa de grupos/participantes y cierre de sesión. El ejemplo financiero de la landing sigue siendo ficticio. Detalles en [client/README.md](client/README.md).

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

Orígenes sin rutas, barra final ni comodines. CORS usa credenciales. En producción la cookie es `__Host-splitly_session`, sin Domain y con Path=/; en desarrollo es `splitly_session`. Se rechazan configuraciones de producción inseguras. Cloudflare Pages usa la Function `/api` descrita abajo: mantener `VITE_API_URL=` vacío y `COOKIE_SAMESITE=lax`. El navegador solo se comunica con Pages; no necesita cookies de terceros de Render. El proxy de Vite sigue disponible únicamente en desarrollo. No mezclar localhost y 127.0.0.1 al probar cookies locales.

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

| Ruta frontend | Función |
|---|---|
| `/dashboard` | Tres grupos propios más recientes, creación y acceso a lista/detalle |
| `/groups` | Todos los grupos, búsqueda por nombre, crear/editar/eliminar con confirmación |
| `/groups/:groupId` | Nombre/fecha reales, editar/eliminar grupo y CRUD de participantes |

Crear un grupo, abrir su tarjeta y añadir participantes. Cancelar/Escape no envía escrituras. Los borrados requieren confirmación; un grupo con participantes devuelve 409 y ofrece un enlace al detalle para retirarlos primero. Cada pantalla se actualiza tras el éxito REST y consulta de nuevo al entrar. Actualizar recoge cambios de otra pestaña; no hay sincronización en tiempo real. La búsqueda local ignora acentos y mayúsculas.

Componentes compartidos en `client/src/components/workspace/`, acceso REST en `services/groups.js`, cargas cancelables en `hooks/useRemoteResource.js`, fechas en `utils/format.js` y estilos `workspace.css`. Se reutilizan cookies/CSRF y cliente HTTP, sin nuevos endpoints, dependencias o migraciones. No se inventan categorías, fotos, saldos ni totales. Gastos y balances siguen pendientes.

`npm test` incluye seis recorridos nuevos de CRUD, navegación, búsqueda, recarga, cancelación, 409 real, grupos ajenos, errores CSRF/validación y sesión revocada, además de los seis de autenticación. Se ejecutan con PostgreSQL temporal real sin eliminar datos de splitly_dev. Revisión manual pendiente: lector de pantalla, zoom 200 %, 320 px, otros navegadores y visitas directas en el dominio HTTPS. Configurar fallback SPA sin reescribir `/api` ni assets a index.html.

Con la migración aplicada manualmente, iniciar API en 8000 y `npm run dev` desde client. Abrir `http://localhost:5173/register`, registrar nombre/correo ficticios y una frase de 15–128 caracteres. Debe llevar a `/dashboard`; recargar mantiene la sesión por `/api/auth/me`. Cerrar sesión lleva a login e invalida la cookie en el servidor; una visita directa a dashboard vuelve a login. Iniciar sesión con el mismo correo recupera únicamente los grupos propios. Ver [docs/API.md](docs/API.md) para Swagger y CSRF.

Backend: `python -m pytest -p no:cacheprovider` y `python -m pip check` desde server. Frontend: `npm run lint`, `npm run build` y `npm test` desde client. Playwright inicia React y FastAPI con PostgreSQL temporal real (puertos 5175/8001), prueba registro/login/recarga/logout y retira su base mediante cierre controlado; no usa la API de desarrollo. Requiere usuario PostgreSQL local con CREATEDB y navegador Edge en Windows; `PLAYWRIGHT_CHANNEL=chrome` permite Chrome instalado. En otros sistemas instalar Chromium con `npx playwright install chromium`. Si se mata el proceso abruptamente, revisar posibles bases temporales restantes antes de retirarlas. Los tests no muestran secretos ni guardan traces de red.

## Despliegue: Cloudflare Pages → Render → Supabase

No se ha desplegado desde esta tarea. Sustituir `TU-PROYECTO.pages.dev`, `TU-API.onrender.com` y los marcadores de conexión por los valores propios, sin versionar secretos.

### 1. Render (Web Service Python)

- Root Directory: `server`.
- Build Command: `python -m pip install -r requirements.txt`.
- Start Command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` (Render proporciona PORT).
- Health Check Path: `/api/health`. Solo comprueba HTTP; no verifica PostgreSQL.
- Runtime Python 3.11+ compatible con requirements.txt; verificar la versión elegida en los logs de build.

Configurar exactamente estas variables del backend en Render:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | Secreto `postgresql+psycopg://USUARIO:CONTRASENA@HOST:5432/postgres?sslmode=require`, usando los datos reales de conexión de Supabase. Codificar usuario/contraseña como componentes URL; usar conexión directa o pool de sesión accesible desde Render, no pool de transacciones para migraciones. No copiar este secreto a Cloudflare/Vite. |
| `ENVIRONMENT` | `production` |
| `COOKIE_SECURE` | `true` |
| `COOKIE_SAMESITE` | `lax` |
| `SESSION_TTL_SECONDS` | `28800` |
| `CORS_ORIGINS` | `https://TU-PROYECTO.pages.dev` (añadir `,https://TU-DOMINIO` si se usan ambos; sin rutas, barra final ni comodines) |
| `CSRF_TRUSTED_ORIGINS` | `https://TU-PROYECTO.pages.dev` y los dominios frontend adicionales; añadir `https://TU-API.onrender.com` solo si se usará Swagger directamente en Render |

No hay SECRET_KEY ni JWT en esta arquitectura. El frontend ya está permitido para CSRF mediante CORS_ORIGINS; repetirlo en CSRF_TRUSTED_ORIGINS es explícito, no obligatorio. **No reemplazar el Origin del navegador por el de Render:** eliminaría la comprobación de origen que necesita el backend.

Antes de usar autenticación/CRUD, revisar respaldo, destino y las migraciones existentes desde un entorno autorizado. Ejecutar manualmente `python -m alembic current`, revisar el SQL indicado en la sección de migraciones y, cuando corresponda, `python -m alembic upgrade head` seguido de `python -m alembic check`. No se cambian modelos ni migraciones; no se aplicaron en Supabase durante esta tarea. `app.db.check` rechaza destinos remotos intencionalmente.

Referencia del comando de arranque: [Render FastAPI](https://render.com/docs/deploy-fastapi).

### 2. Cloudflare Pages

Crear/configurar un proyecto **Pages** con integración Git (no un Worker estático):

- Root Directory: `client`.
- Build Command: `npm run build`.
- Build Output Directory: `dist` (relativa a `client`).
- Node.js: `NODE_VERSION=24` en variables de compilación.
- `VITE_API_URL=`: valor vacío en compilación. Quitar cualquier valor absoluto heredado y recompilar. No poner `/api` como valor: el cliente ya lo añade.
- Binding de entorno para **Pages Functions**: `API_ORIGIN=https://TU-API.onrender.com`, solo el origen HTTPS, sin `/api`, credenciales, query ni fragmento. El valor se usa en ejecución; no es `VITE_API_ORIGIN`. API_ORIGIN no necesita ser secreto, pero nunca añadir DATABASE_URL, contraseñas ni tokens al frontend.
- Configurar variables de Production y, si se habilitan, Preview por separado. Para previews usar una API/base de pruebas y orígenes exactos permitidos; no habilitar comodines CSRF para URLs efímeras.
- Compatibility date de Functions: `2026-10-23` (runtime local verificado con Wrangler 4.153.0).
- No añadir reglas «Cache Everything» que incluyan `/api/*`; todas sus respuestas son `Cache-Control: no-store`.

Pages detecta `client/functions/api/[[path]].js` desde la raíz `client`, fuera de dist. `client/functions/api.js` cubre también `/api` exacto. `public/_routes.json` se copia a dist y limita las Functions a `/api` y `/api/*`; las demás rutas continúan como assets/SPA. No añadir un `404.html` en la raíz de dist ni una Function catch-all: Pages usa su fallback SPA para `/login`, `/register`, `/dashboard`, `/groups` y `/groups/:groupId`. No hacen falta redirects globales ni rewrites `/api → index.html`.

La carga manual por arrastrar **solo dist** no publica estas Functions. Usar integración Git o, de forma manual y cuando se autorice, Wrangler desde client con acceso al proyecto. Esta tarea no ejecuta comandos de publicación.

Fuentes: [rutas de Functions](https://developers.cloudflare.com/pages/functions/routing/), [variables de ejecución](https://developers.cloudflare.com/pages/functions/bindings/), [fallback SPA](https://developers.cloudflare.com/pages/configuration/serving-pages/).

### 3. Qué conserva el proxy

Reenvía método, ruta completa `/api/...`, query, cuerpo sin interpretar, Cookie, Origin, Referer, Content-Type y X-CSRF-Token. El destino depende únicamente de API_ORIGIN; parámetros/headers del cliente no pueden elegir otro servidor. Elimina Host y cabeceras hop-by-hop, sustituye los X-Forwarded-* enviados por el cliente y no inventa Origin/CSRF. Conserva códigos 201/204/401/403/409/422, cuerpos y todas las cabeceras Set-Cookie sin unirlas por comas.

Las redirecciones de API no se siguen en el servidor con credenciales: las redirecciones internas a `/api` se reescriben hacia Pages conservando el estado (por ejemplo 307); las externas o fuera de API se rechazan con 502. Fallos de conexión devuelven JSON 502; configuración inválida, JSON 500. Nunca se devuelve HTML de la SPA para un error de API.

| Atributo de cookie | Compatibilidad con Pages |
|---|---|
| `Secure` | Obligatorio; visitar Pages por HTTPS. No desactivarlo para producción. |
| `HttpOnly` | Se conserva; React no lee la sesión. CSRF llega por JSON y vive solo en memoria. |
| `SameSite=lax` | Compatible: el navegador llama al mismo origen Pages, no a Render. No se requiere `none`. |
| `Path=/` | Se conserva tanto al emitir como al borrar cookie. Requisito del prefijo `__Host-`. |
| Sin `Domain` | La cookie se asocia al host de Pages que entrega la respuesta, no al host Render. No añadir Domain de Render ni reescribir cookies. |

Esta compatibilidad se deduce de los atributos actuales y se comprueba en pruebas de cabeceras; **no equivale a haber probado almacenamiento/uso de cookies en los dominios reales**. Una sesión en pages.dev no se comparte con un dominio personalizado; usar un dominio canónico y probar cada host autorizado.

### 4. Verificación antes de dar producción por lista

Desde client: `npm run test:proxy`, `npm run lint`, `npm run build`. Las pruebas Node del proxy sustituyen el upstream por respuestas controladas: comprueban transporte y cabeceras, no una sesión real. `npm test` prueba el flujo React/FastAPI/PostgreSQL local existente, no el runtime de Pages ni Render.

Para validar además el empaquetado de Functions sin desplegar: `npx --yes wrangler@4 pages functions build --outdir .pages-build` desde client. Para ensayar Pages localmente: `npx --yes wrangler@4 pages dev dist --compatibility-date=2026-10-23 --binding API_ORIGIN=https://TU-API-DE-PRUEBAS.onrender.com`; usar API/base de pruebas y autorizar su origen local exacto solo en ese entorno. Cookies Secure de producción requieren ensayo HTTPS, no bajar su seguridad.

Prueba de routing sin contactar ninguna API: iniciar `npx --yes wrangler@4 pages dev dist --ip 127.0.0.1 --port 8788 --compatibility-date=2026-10-23 --binding API_ORIGIN=http://invalid.example` y, en otra terminal desde client, ejecutar `node proxy-tests/pages-smoke.js`. La configuración inválida es deliberada: las seis rutas SPA deben responder HTML 200 y las cuatro rutas API JSON 500/no-store. No usar ese valor de API_ORIGIN en producción.

En el **dominio HTTPS real**, después de un despliegue manual:

1. Abrir `/api/health`: JSON, nunca index.html. Verificar también que `/api/no-existe` devuelve JSON 404 y `/api` no devuelve la SPA.
2. Visitar directamente `/login`, `/register`, `/dashboard`, `/groups` y un detalle; recargar. Las rutas privadas redirigen si falta sesión.
3. Registrar un usuario ficticio y confirmar en Network que la URL es `https://TU-FRONTEND/api/auth/register`, devuelve 201 y Set-Cookie conserva `__Host-splitly_session; Secure; HttpOnly; SameSite=lax; Path=/`, sin Domain. Revisar en Application que el navegador la aceptó; `document.cookie` no la muestra.
4. Recargar: `/api/auth/me` devuelve 200 y CSRF. Crear, listar, editar y borrar un grupo ficticio; añadir/editar/borrar participantes. Revisar Origin del frontend y X-CSRF-Token en escrituras. Un grupo con participantes debe mantener 409 hasta retirar sus miembros.
5. Con sesión válida, repetir una escritura sin CSRF o con Origin ajeno desde una herramienta de pruebas: debe ser 403. No «arreglarlo» reescribiendo Origin. Conservar los secretos de las peticiones solo en memoria, sin capturas/traces compartidos.
6. Logout debe devolver 204 y borrar la cookie con los mismos atributos. `/api/auth/me` debe dar 401; reutilizar la cookie previa en un cliente de prueba debe dar 401 por revocación. Login posterior debe crear una nueva sesión.
7. Confirmar que respuestas autenticadas no llegan desde caché y no hay redirecciones del navegador hacia Render. Repetir en al menos dos navegadores y con bloqueo de cookies de terceros.

Siguen pendientes las medidas de apertura pública ya documentadas (incluido límite de intentos), la conexión real a Supabase y este recorrido HTTPS en los dominios finales. No se afirma que producción esté validada solo por compilar.
