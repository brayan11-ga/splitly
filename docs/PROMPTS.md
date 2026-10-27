# Registro de prompts usados

Registrar solo prompts realmente enviados y sus resultados. Campos: fecha/hora, herramienta, objetivo, prompt textual o enlace, archivos alterados, pruebas, resultado, correcciones manuales.

## Plantilla
- Fecha:
- Herramienta/modelo:
- Objetivo:
- Prompt:
- Archivos afectados:
- Verificación:
- Resultado / limitaciones:

## 2026-10-27 — Esqueleto del backend
- Herramienta: Codex.
- Objetivo: implementar el esqueleto funcional sin modificar el frontend.
- Prompt textual recibido:

```text
Actúa como un desarrollador backend senior especializado en Python, FastAPI, Pydantic, SQLModel y PostgreSQL.

Estamos construyendo Splitly, una aplicación web para gestionar gastos compartidos.

Lee primero AGENTS.md, README.md y los documentos dentro de docs/. Estos archivos representan las decisiones de arquitectura del proyecto.

**Objetivo de esta iteración: implementar el esqueleto funcional del backend.**

1. Inspecciona la estructura actual del proyecto.
2. Crea dentro de server/app/ una arquitectura modular con routers, models, schemas, services y db.
3. Configura FastAPI con un punto de entrada main.py.
4. Implementa GET /api/health, que retorne un JSON indicando que la API funciona.
5. Configura CORS para permitir el origen local de React durante el desarrollo.
6. Prepara la configuración de conexión con PostgreSQL mediante DATABASE_URL, sin incluir credenciales reales en el código.
7. Crea un archivo .env.example con variables de ejemplo.
8. Añade tests con pytest para comprobar el endpoint de salud.
9. Genera un requirements.txt con las dependencias del backend.
10. Actualiza la documentación cuando sea necesario.

**Reglas:**
- No modifiques el frontend todavía.
- No implementes autenticación.
- No inventes credenciales de Supabase.
- No uses datos en memoria como persistencia definitiva.
- No introduzcas nuevas dependencias innecesarias.
- No sobreescribas documentación existente sin revisarla.
- No crees ni publiques repositorios remotos.
- Trabaja únicamente dentro de este proyecto.

Al finalizar:
- Ejecuta los tests disponibles.
- Indica qué archivos creaste o modificaste.
- Explica cómo iniciar el servidor.
- Reporta errores encontrados.
- Sugiere la siguiente implementación, pero no la ejecutes todavía.

Responde en español.
```

- Archivos afectados: `server/app/` (configuración, entrada, routers, schemas, db y paquetes models/services), `server/tests/test_health.py`, `server/pytest.ini`, `server/requirements.txt`, `server/.env.example`; README y documentos API, ARQUITECTURA, DECISIONES, EVIDENCIAS y este registro.
- Verificación: desde `server/`, `.venv\Scripts\python.exe -m pytest`: 5 pruebas aprobadas; advertencia de permisos al escribir la caché de pytest.
- Verificación adicional: `python -m pytest -p no:cacheprovider`: 5 pruebas aprobadas sin advertencias; `python -m pip check`: sin dependencias incompatibles. Motor PostgreSQL/psycopg construido con URL ficticia sin abrir conexión. `git diff --check` sin errores en archivos rastreados (el proyecto está aún sin rastrear en Git). Entorno utilizado: Python 3.14.5; no se verificó por separado Python 3.11.
- Resultado / limitaciones: salud, CORS y OpenAPI verificados con TestClient. Sin conexión real a PostgreSQL, tablas, CRUD ni lógica de cálculo. Se corrigió la referencia antigua a Express en el pitch existente.

## 2026-10-27 — Dos entornos PostgreSQL y Alembic
- Herramienta: Codex.
- Objetivo: configurar desarrollo local splitly_dev y futura producción Supabase, modelos Group/Member, migración inicial y comprobación local.
- Extractos textuales del prompt real recibido (mensaje completo en la conversación):

```text
Actúa como ingeniero backend senior especializado en Python, FastAPI, SQLModel, PostgreSQL y Alembic.

Estamos desarrollando Splitly. Ya tenemos FastAPI funcionando y ahora queremos implementar una estrategia de base de datos con dos entornos:

- Desarrollo: PostgreSQL local en Windows, base de datos splitly_dev.
- Producción: PostgreSQL alojado en Supabase.
```

```text
Restricciones:
- No conectarse todavía a Supabase.
- No crear ni modificar bases de datos externas.
- No borrar tablas o datos existentes.
- No ejecutar migraciones destructivas.
- No utilizar SQLite como base principal.
- No modificar el frontend.
- No incluir contraseñas en archivos versionados.
- Si la conexión local no está disponible, informa el problema sin inventar un resultado exitoso.
```

- Archivos afectados: `.gitignore`, `server/.env.example`, `server/requirements.txt`, `server/pytest.ini`, `server/app/db/session.py`, `server/app/db/check.py`, `server/app/models/`, `server/alembic.ini`, `server/alembic/`, `server/tests/test_database.py`, README, ARQUITECTURA, DECISIONES y este registro.
- Verificaciones: 10 pruebas aprobadas desde server, `alembic heads` reconoce `0001_groups_members`, `pip check` sin incompatibilidades y `git check-ignore -v` confirma exclusión de .env, claves y respaldos. `git ls-files` no mostró archivos sensibles rastreados. SQL inicial generado offline y comparado con metadata en pytest, sin conexión ni cambios de tablas.
- Incidencias: instalación inicial de Alembic bloqueada; reintento con permiso instaló Alembic 1.20.1 y Mako. Faltan DATABASE_URL y server/.env: `python -m app.db.check` termina con código 1 sin conexión. Servicio PostgreSQL Windows activo, sin verificar acceso ni existencia de splitly_dev. Una ejecución desde la raíz encontró una carpeta antigua de caché sin permisos; se excluye su patrón en pytest.ini sin borrarla.
- Límites: sin conexión a Supabase, sin aplicar migraciones, sin CRUD ni cálculos. Pruebas con Python 3.14.5; Python 3.11 no verificado por separado.

## 2026-10-27 — CRUD persistente de grupos y participantes
- Herramienta: Codex.
- Objetivo: implementar los nueve endpoints REST de grupos y participantes sobre los modelos y sesiones existentes, sin frontend ni git push.
- Extractos textuales del prompt real recibido (mensaje completo en esta conversación):

```text
OBJETIVO:
Implementar el CRUD completo de grupos y participantes en FastAPI.

ENDPOINTS DE GRUPOS:
- POST /api/groups
- GET /api/groups
- GET /api/groups/{group_id}
- PATCH /api/groups/{group_id}
- DELETE /api/groups/{group_id}

ENDPOINTS DE PARTICIPANTES:
- POST /api/groups/{group_id}/members
- GET /api/groups/{group_id}/members
- PATCH /api/groups/{group_id}/members/{member_id}
- DELETE /api/groups/{group_id}/members/{member_id}
```

```text
PRUEBAS:
- Crear, listar, consultar, editar y eliminar grupos.
- Crear, listar, editar y eliminar participantes.
- Verificar errores 404 y 422.
- Verificar integridad referencial.
- Utilizar una base de datos de pruebas aislada; nunca borrar información de splitly_dev para realizar pruebas.
```

- Archivos afectados: `server/app/main.py`; nuevos repositories, routers groups/members y dependencia compartida, schemas groups/members, servicios groups/members/errors; `server/tests/conftest.py`, `server/tests/test_crud.py`; README, API, ARQUITECTURA, DECISIONES y este registro.
- Decisiones: nombres estrictos no vacíos con espacios exteriores recortados; PATCH requiere name y rechaza campos ajenos. Grupo con participantes devuelve 409 hasta retirar explícitamente sus participantes. Pertenencia incorrecta devuelve 404. No se modificaron modelos ni migraciones.
- Verificación: `python -m pytest -p no:cacheprovider` desde server: 40 pruebas aprobadas con PostgreSQL local real, incluyendo FK y persistencia confirmada desde otra conexión. Se creó una base aleatoria exclusiva splitly_test_<UUID>, se aplicó allí la migración existente y se retiró al finalizar; sin modificar datos de splitly_dev. Los tests HTTP se aíslan mediante transacciones/savepoints. No se usó SQLite ni persistencia en memoria.
- Correcciones: README referenciaba server/.env.example, ausente en el árbol actual; se corrigió para usar las variables del ejemplo versionado en la raíz sin sobrescribir .env. No se imprimieron credenciales.
- Límites: sin gastos, cálculos, autenticación, paginación ni cambios frontend. No hubo conexión a Supabase ni push a GitHub. Entorno verificado: Python 3.14.5; no se probó Python 3.11 por separado.
