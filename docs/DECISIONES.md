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

## 2026-10-27 — CRUD de grupos y participantes
- Se reutilizan Group, Member y get_session sin alterar modelos ni agregar migraciones. Routers HTTP, esquemas Pydantic, servicios con transacciones explícitas y consultas en `db/repositories.py`.
- Nombre obligatorio en creación y PATCH, texto estricto recortado y no vacío; campos adicionales rechazados. PATCH solo edita el nombre; se mantienen nombres duplicados permitidos por el esquema actual.
- Participantes bajo `/api/groups/{group_id}/members/{member_id}`; acceder desde otro grupo devuelve 404. Listas ordenadas por created_at/id.
- Borrado de grupos con participantes rechazado con 409, sin cascada ni pérdida implícita de datos. El cliente debe eliminar primero cada participante. Las restricciones FK siguen protegiendo la integridad; conflictos de escritura revierten la transacción y no filtran mensajes del driver.
- Pruebas PostgreSQL en una base local aleatoria `splitly_test_<UUID>` creada y retirada exclusivamente por la ejecución. Se aplica la migración existente solo allí. Transacciones externas y savepoints aíslan las pruebas HTTP; una prueba con conexión independiente verifica el commit real. No se escribe ni se borra en splitly_dev.

## 2026-10-27 — Landing pública editorial
- Landing React separada en páginas, layout y primitivas reutilizables. Solo rutas públicas `/`, `/login`, `/register` y fallback; las dos rutas de acceso son provisionales y no tienen formularios.
- Se adapta el HTML y la captura de Stitch; se usa como fuente de tokens el YAML de DESIGN.md (lima #bff52a y lavanda #c0c1ff), que difiere de algunos colores de su prosa. Identidad propia sin recursos de Lando Norris.
- Tailwind mediante plugin Vite, Motion para entradas progresivas y microinteracciones, fuentes locales Fontsource. Se mantienen React y Vite existentes.
- React Bits evaluado: una aparición de texto ligera duplicaría la función de Motion; los fondos WebGL no aportan suficiente valor en esta iteración. Se conserva una decoración geométrica CSS estática y no se agrega React Bits ni 3D.
- Preferencia de movimiento reducido, enlace para saltar al contenido, foco visible y navegación de secciones disponible también en móvil.
- Se retiran del original estadísticas no verificadas, garantías comerciales, exportaciones, tiempo real y botones de pagos simulados. Ejemplo fijo de COP 90.000 entre tres personas, marcado como ficticio. No existe lógica financiera nueva ni almacenamiento en el navegador.
- No se modifica FastAPI ni CORS. Su revisión de orígenes de producción sigue pendiente antes del despliegue según README.
- El hosting del cliente deberá resolver rutas SPA hacia index.html. No se despliega ni se ejecuta git push.

## 2026-10-27 — Interacciones progresivas de la landing
- Se reutilizan Motion y CSS sin instalar GSAP, Three.js ni otras dependencias. Se conservan textos, colores, composición, navegación y backend.
- Nuevos componentes MagneticLink, InteractiveCard, HeroSurface y ContextLink; hook compartido para capacidades y springs. Transformaciones acotadas, indicador contextual local y decorativo, sin sustituir el cursor del sistema.
- Se mantiene una envolvente estable alrededor del CTA magnético para ampliar la detección de proximidad sin desplazar el layout; foco de teclado restablece el movimiento. Las tarjetas no reciben roles interactivos ni tabindex porque no ejecutan acciones.
- Eventos de puntero locales; Motion values evitan renders React por cada movimiento. La suscripción de media query se limpia al desmontar; cambio a movimiento reducido o puntero no apto reinicia los springs.
- Táctil y movimiento reducido sin efectos de puntero. Foco visible y estados active conservados. Revisión manual documentada en client/README.md; no se afirma una auditoría visual automatizada.

## 2026-10-27 — Autenticación completa y propiedad de grupos
- La solicitud explícita actual sustituye la decisión de no autenticar el MVP; se actualiza AGENTS para reflejarlo. Se conservan Landing, estilos e interacciones recientes, incluidos cambios sin commit.
- SQLModel User con email normalizado y restricción UNIQUE/CHECK en PostgreSQL. Argon2id mediante pwdlib, frases de 15–128 caracteres sin reglas artificiales de composición ni truncado. Login verifica un hash ficticio también para usuarios inexistentes y devuelve el mismo 401 para credenciales incorrectas, siguiendo el [patrón de FastAPI](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/tutorial/security/oauth2-jwt.md).
- Sesiones opacas aleatorias de 256 bits en cookie HttpOnly; PostgreSQL conserva solo su SHA-256 y vencimiento absoluto. Logout borra el registro y login rota la sesión actual. Se evita JWT para permitir revocación inmediata sin listas adicionales; no hay clave global de firma ni secretos predeterminados de producción.
- CSRF: Origin exacto y cabecera personalizada en acceso público; CSRF ligado a la sesión para escrituras privadas. CORS sin comodines y con credenciales; SameSite es defensa adicional, según [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html). Cookie Secure y prefijo __Host- en producción; validación de configuración falla si producción usa HTTP o cookie insegura.
- Migración 0002 aditiva: no asigna dueños arbitrariamente ni elimina datos. Grupos anteriores con NULL quedan conservados y ocultos hasta asignación administrativa verificada; nuevas altas usan el propietario autenticado. Ningún payload puede cambiar owner_id. Recursos ajenos responden 404 para reducir enumeración; 409 de grupo con participantes se conserva.
- React usa AuthProvider, /me, fetch credentialed y CSRF solo en memoria; sin localStorage/sessionStorage para secretos. Formularios inspirados en Stitch con etiquetas, foco, confirmación, errores y loading; no se copian garantías AES-256/auditorías, estadísticas ficticias, recuperación de contraseña ni botones sociales sin funcionalidad.
- Playwright se incorpora únicamente como dependencia de desarrollo para pruebas reales React/FastAPI/PostgreSQL; los tests usan bases temporales independientes, migración de datos anteriores y navegador Edge instalado, sin modificar splitly_dev. Capturas sintéticas de formularios sin contraseña en resultados ignorados por Git; traces/videos desactivados.
- Pendientes de producción: rate limiting persistente/gateway, recuperación y verificación de correo, TLS/dominios reales, política de limpieza de sesiones expiradas y revisión de despliegue. Registro duplicado devuelve 409 por requisito y permite inferencia de disponibilidad del email. No se presenta como auditoría de seguridad ni se publica/pushea.

## 2026-10-27 — Gestión completa de grupos y participantes en React
- Se conserva la API y autenticación existentes. Los diseños Mis grupos/Detalle Stitch se adaptan a name/id/created_at y group_id, sin categorías, imágenes, saldos, gastos o funciones financieras inexistentes.
- Componentes compartidos para navegación, tarjetas, cargas y formularios/confirmaciones. Diálogo HTML nativo con foco modal, Escape y restauración de foco; Motion breve según reduced motion. Sin nuevas dependencias ni Three.js.
- Estado transitorio actualizado tras confirmar REST; consulta fresca al entrar y botón Actualizar para cambios externos. Sin persistencia local ni promesas de sincronización entre pestañas en tiempo real.
- 409 conserva el grupo y conduce a gestionar participantes; confirmación explícita para ambos tipos de borrado. Los formularios solo envían name y nunca owner_id.
- Dashboard resume tres grupos recientes; /groups contiene lista/búsqueda y /groups/:groupId gestiona grupo/participantes. Búsqueda local insensible a acentos y mayúsculas.
- Se amplían las pruebas reales React/FastAPI/PostgreSQL temporal y se mantienen las de autenticación. Sin cambios de backend, migraciones, datos de splitly_dev o push.

## 2026-10-27 — Proxy de mismo origen en Cloudflare Pages
- Cliente HTTP conserva credentials:include y X-CSRF-Token; VITE_API_URL vacío. Vite local permanece intacto.
- Functions en client/functions/api/[[path]].js y api.js para la ruta exacta; public/_routes.json limita invocaciones a /api y /api/*. Fallback SPA nativo de Pages fuera de API, sin 404.html ni rewrite global.
- API_ORIGIN es un binding de ejecución HTTPS sin ruta/query/credenciales. Ningún parámetro, cabecera o ruta del usuario controla el destino. Headers Host/hop-by-hop retirados; Origin, Cookie y CSRF conservados, sin fabricar confianza. Cuerpos sin interpretar y respuestas no-store.
- Set-Cookie se copia como colección Headers, sin unir por comas ni modificar Secure/HttpOnly/SameSite/Path/Domain. Cookie __Host- host-only emitida a través de Pages; SameSite=lax compatible con /api en el mismo origen. Compatibilidad por contrato no equivale a validación de cookies en producción.
- Fetch con redirect manual: redirecciones internas API vuelven al dominio del frontend, externas se bloquean; no se siguen redirecciones enviando cookies a terceros. Errores de conexión/configuración genéricos y sin logs de credenciales.
- Pruebas Node sin nuevas dependencias para transporte/headers y regresión Playwright existente con PostgreSQL temporal; no se modifica backend, modelos, migraciones, gastos ni balances. No se aplica migración, push o despliegue. Configuración exacta de Render/Pages y recorrido HTTPS pendiente en README.
