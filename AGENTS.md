# Instrucciones para Codex — Splitly

## Contexto
Hackathon: MVP de gastos compartidos, con `client/` React + Vite + Tailwind y `server/` Python FastAPI + SQLModel + PostgreSQL Supabase. El backend NO usa Express ni Node.js. React Bits, Motion y React Three Fiber son mejoras visuales graduadas.

## Reglas obligatorias
- Lee README.md, docs/REQUISITOS.md, docs/ARQUITECTURA.md y docs/API.md antes de programar.
- Entrega cambios pequeños verificables, informa archivos modificados, comandos ejecutados y límites.
- Separar UI, acceso a API, lógica de cálculos, rutas, servicios, validación y persistencia.
- Frontend React con componentes funcionales, responsive y accesibles. Maneja estados loading, error, empty y success.
- Backend Python 3.11+, FastAPI, Pydantic, SQLModel, pruebas pytest. Swagger en `/docs`.
- No exponer DATABASE_URL, claves secretas ni tokens en Vite. `.env` fuera de Git.
- Sin autenticación en MVP; solo datos ficticios, no anunciar seguridad multiusuario.
- Dinero: enteros `amount_cents`, moneda COP, reparto equitativo y remanente determinista.
- Validar integridad del grupo, pagador, participantes y cantidades; errores HTTP apropiados.
- No almacenar datos solo en arrays o localStorage; usar PostgreSQL.
- Animaciones progresivas: primero CRUD/persistencia; Motion/React Bits después; 3D solo si el MVP ya funciona.
- Respetar `prefers-reduced-motion`, controles de teclado, responsive y carga diferida de 3D. No bloquear los formularios con animaciones.
- Ejecutar pruebas de cálculo, y revisar CORS para producción.
- Actualizar docs/DECISIONES.md tras decisiones y docs/PROMPTS.md con prompts reales (no inventar evidencia).
