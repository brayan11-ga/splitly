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

## 2026-10-27 — Landing React desde Google Stitch
- Herramienta: Codex.
- Objetivo: implementar solo la landing pública con adaptación responsive y navegación provisional de acceso.
- Extractos textuales del prompt real recibido (mensaje completo en esta conversación):

```text
Implementar la Landing Page pública de Splitly en React basándose en el diseño de Google Stitch.

La inspiración creativa es la web de Lando Norris, pero conservando una identidad propia, sin copiar recursos visuales o elementos distintivos.
```

```text
ALCANCE:
- Implementar solo la Landing Page.
- No implementar autenticación todavía.
- No modificar el backend FastAPI.
- No implementar dashboard ni formularios de login y registro.
- Las rutas /login y /register podrán mostrar páginas provisionales claramente identificadas como pendientes.
- No agregar efectos 3D pesados en esta iteración.
- No incluir información sensible ni credenciales.
```

- Inspección: AGENTS, README, todos los documentos de docs, DESIGN.md, HTML y screen.png de la landing.
- Archivos afectados: client/src/App.jsx, App.css, index.css, components/LandingUI.jsx, components/SiteLayout.jsx, pages/LandingPage.jsx, pages/PendingPage.jsx, client/index.html, public/favicon.svg, vite.config.js, package.json y lock; client/README.md, README y docs/DECISIONES.md, PROMPTS.md.
- Implementación: hero, pasos, ejemplo COP, beneficios, CTA; Motion y navegación provisional. Evaluación de React Bits documentada en DECISIONES.
- Incidencia: npm inicial bloqueado por caché sin paquetes; reintento de descarga solicitado mediante permiso del entorno.
- Verificación final: `npm run build` desde client aprobada (446 módulos; JS 402,69 kB / 129,10 kB gzip; CSS 19,49 kB / 5,20 kB gzip). `npm run lint` desde client aprobada sin advertencias. `git diff --check` sin errores de whitespace (Git avisa conversión futura LF/CRLF).
- Correcciones: compilación inicial bloqueada por spawn EPERM del sandbox; compilación autorizada fuera del sandbox aprobada. Se corrigió una advertencia de render impuro por Date usando el año de esta edición. Una llamada accidental de lint desde la raíz falló por ausencia de package.json; se repitió correctamente desde client.
- Límites: no se ejecutó un navegador ni se generaron capturas de implementación; revisión manual pendiente según client/README.md. No hay pruebas de cálculo en server/tests ni lógica financiera nueva en esta iteración; el reparto mostrado es un ejemplo estático, no un motor validado. Backend intacto, sin push ni despliegue.

## 2026-10-27 — Landing interactiva con Motion
- Herramienta: Codex.
- Objetivo: añadir magnetismo, tarjetas reactivas, parallax de hero, indicador contextual y microinteracciones manteniendo diseño y rutas.
- Extractos textuales del prompt real recibido (completo en esta conversación):

```text
Transformar la Landing Page actual en una experiencia mucho más interactiva e inmersiva, mediante animaciones que reaccionen a las acciones del usuario.
```

```text
- Usar Motion y CSS para la mayoría de efectos.
- Crear componentes reutilizables.
- Usar transformaciones GPU-friendly cuando sea posible.
- Evitar listeners globales innecesarios.
- No producir renders React continuos por cada movimiento del ratón.
- Desactivar efectos dependientes de hover en dispositivos táctiles.
- Respetar prefers-reduced-motion.
- Mantener indicadores visibles de foco para teclado.
- Evitar modificar el layout durante las animaciones.
```

- Archivos: client/src/components/PointerInteractions.jsx (nuevo), client/src/hooks/usePointerMotion.js (nuevo), LandingUI.jsx, pages/LandingPage.jsx, App.css; client/README.md, docs/DECISIONES.md y PROMPTS.md.
- Límites: sin cambios de backend, autenticación ni dependencias. Sin push. Revisión visual y táctil pendiente en navegador según client/README.md; sin nueva lógica de cálculo ni pruebas de cálculo existentes que ejecutar en esta iteración.
- Verificación final: `npm run lint` desde client aprobado sin advertencias; `npm run build` aprobado (448 módulos, JS 409,23 kB / 131,42 kB gzip, CSS 21,89 kB / 5,70 kB gzip). Build inicial bloqueado por spawn EPERM; reintento autorizado fuera del sandbox aprobado. Lint invocado inicialmente desde raíz falló por no existir allí package.json y se ejecutó correctamente desde client.
- `git diff --check`: se corrigió una línea vacía al final de LandingPage.jsx. Los avisos de conversión LF/CRLF pertenecen a la configuración de Git. Sin cambios en backend ni manifiestos de dependencias.
- No se ejecutó navegador; no se presentan capturas, mediciones de fluidez ni pruebas visuales inventadas. Procedimiento manual en client/README.md.

## 2026-10-27 — Autenticación PostgreSQL a React
- Herramienta: Codex.
- Objetivo: autenticación real con Argon2, sesiones revocables en cookie HttpOnly, CSRF, autorización por propietario, formularios Stitch y dashboard protegido. La solicitud actual sustituye la regla anterior de MVP sin autenticación.
- Extractos textuales del prompt real (completo en la conversación):

```text
OBJETIVO PRINCIPAL:
Implementar un sistema REAL y FUNCIONAL de autenticación completo, desde PostgreSQL hasta React.

IMPORTANTE: tenemos poco tiempo para finalizar el hackathon. Prioriza una implementación segura, sencilla, verificable y lista para integrarse con el despliegue.
```

```text
6. Si existen grupos anteriores sin propietario, tratarlos mediante una estrategia de migración explícita y segura. No asignarlos arbitrariamente a usuarios nuevos ni eliminar datos.
```

```text
- Usar sesión autenticada mediante cookie HttpOnly.
- Configurar Secure y SameSite apropiadamente para desarrollo local y producción.
- No almacenar JWT o secretos de sesión en localStorage ni sessionStorage.
- Implementar una dependencia get_current_user.
```

```text
- Implementa por etapas dentro de esta misma tarea.
- Verifica los resultados al terminar cada fase.
- Si alguna decisión afecta datos existentes o requiere secretos reales, prepara el código y documenta el paso manual necesario sin inventar credenciales.
- No modifiques ni destruyas datos existentes de splitly_dev.
- No ejecutes migraciones sobre producción.
- No hagas git push automáticamente.
- No introduzcas servicios externos de autenticación.
```

- Inspección: AGENTS, README y docs; modelos, servicios, routers, sesiones, migración 0001 y pruebas; rutas React y cambios sin commit de Landing/interacciones; DESIGN.md, HTML y capturas Stitch de login/registro.
- Backend: modelos User/AuthSession, Group.owner_id, revisión 0002 aditiva, schemas/router/servicios/repositorio de autenticación, get_current_user con CSRF, filtros de propietario en CRUD, configuración cookies/orígenes, CORS credentialed, validación sin input sensible y respuestas no-store. pwdlib[argon2] y email-validator en requirements. Tests previos adaptados para autenticar; nuevas pruebas de migración preservando datos anteriores, credenciales, revocación, expiración, CSRF, pertenencia y cookies de producción.
- Frontend: servicios API/auth, AuthProvider/ProtectedRoute, AuthPage y DashboardPage, estilos separados en auth.css, rutas, navegación autenticada y proxy Vite. LandingPage, LandingUI, App.css y componentes/hooks de interacciones existentes conservados sin editar en esta tarea. Se respetaron los cambios de documentación recientes al añadir nuevas entradas.
- Verificación por fases: primera fase backend 55 pruebas aprobadas en PostgreSQL temporal real; primera compilación React aprobada tras permiso de ejecución fuera del sandbox. Seis pruebas Playwright aprobadas con Edge, React/FastAPI/PostgreSQL reales, registro/login/recarga/logout revocado, errores, rutas privadas y formularios desktop/móvil. Se inspeccionaron las capturas login-desktop y register-mobile de test-results (ignoradas por Git, sin contraseñas visibles). API auxiliar solo en server/tests, con cierre controlado que retira la base temporal.
- Incidencias resueltas: descarga inicial de pwdlib y Playwright bloqueada por entorno/caché, reintentos autorizados completados; build y navegador bloqueados inicialmente por spawn EPERM, ejecutados con aprobación fuera del sandbox. Advertencia inicial de setState en efecto resuelta antes de lint final. Un parche no coincidió con el BOM de SiteLayout: no se aplicó parcialmente y se reintentó con contexto correcto.
- Archivos adicionales: ejemplos .env separados server/client, configuración y tests Playwright, auxiliar browser_server, .gitignore para resultados, AGENTS, README, client/README y documentos API/ARQUITECTURA/DECISIONES/PROMPTS. Los cambios ajenos del árbol se preservan; el ejemplo raíz apareció eliminado durante el trabajo y no se restauró.
- Límites: ninguna migración o asignación de propietarios ejecutada en splitly_dev ni producción. El procedimiento manual está en README. Sin push, proveedores externos ni secretos reales generados. Faltan medidas de operación pública (rate limiting persistente, recuperación/verificación de correo, TLS/dominios y auditoría del despliegue); no se afirma preparación integral para producción. No se implementan gastos/cálculos ni CRUD visual completo del dashboard.
- Verificación final: pytest 56/56 (incluida cookie Secure/__Host- de producción), pip check sin incompatibilidades, npm run lint sin advertencias, npm run build aprobado (456 módulos, JS 421,07 kB / 134,91 kB gzip). Segunda ejecución Playwright: 6/6 con API/DB reales, incluyendo un grupo creado en PostgreSQL y mostrado al recargar dashboard; proceso API terminó limpiamente. git diff --check sin errores de whitespace; avisos LF/CRLF de Git y avisos de movimiento reducido/NO_COLOR del entorno no bloqueantes. .env de server/client y test-results excluidos por Git; sin archivos de secretos rastreados en las extensiones comprobadas. Python 3.14.5 y Edge en Windows; otros navegadores y entorno de producción no verificados.
