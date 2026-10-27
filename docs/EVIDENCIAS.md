# Evidencias para la presentación

- [ ] Captura del diseño original en Google Stitch (adjuntar archivo/enlace)
- [ ] Captura de la interfaz implementada y comparación con Stitch
- [ ] Demostración de creación de grupos y participantes
- [ ] Demostración de gastos y balances correctos
- [ ] Captura de tabla de PostgreSQL con datos persistidos (sin credenciales)
- [ ] URL pública de frontend funcionando
- [ ] Prueba de API y validación de errores
- [ ] Historial de commits y prompts utilizados

## Pitch de 2 minutos
1. Problema: repartir gastos en viajes y viviendas resulta confuso.
2. Solución: registrar gastos y calcular deudas en una web responsive.
3. Demo: grupo → gasto → saldo → liquidación.
4. Stack: React/Vite + FastAPI/SQLModel + PostgreSQL en Supabase.
5. IA: Stitch para diseño, Codex para implementación y revisión, ChatGPT para planeación.
6. Aprendizajes y próximos pasos: autenticación y reparto personalizado.

## 2026-10-27 — Verificación de la landing pública
- Diseño original inspeccionado: `design/stitch/splitly_landing_page_desktop/screen.png` y `code.html`; sistema en `design/stitch/DESIGN.md`.
- `npm run build` y `npm run lint`, desde client: aprobados. Compilación ejecutada con autorización fuera del sandbox tras EPERM.
- Pendiente: captura de la implementación y comparación visual en navegador; no se afirma validación visual ni accesibilidad auditada automáticamente.
- La landing no demuestra persistencia ni pagos; contiene datos ilustrativos y rutas de acceso provisionales.

## 2026-10-27 — Proxy Pages preparado, producción pendiente
- Node: 12/12 pruebas de handler con upstream controlado (headers, cookies múltiples, CSRF, métodos/cuerpos, errores y redirecciones).
- Playwright: 12/12 flujos locales React/FastAPI/PostgreSQL temporal; no pasan por Pages.
- Lint/build aprobados; Wrangler 4.153.0 compila las Functions sin desplegar.
- Runtime Pages local: seis rutas SPA HTML 200 y cuatro API JSON 500/no-store con binding intencionalmente inválido; no se contacta Render. Script reproducible en client/proxy-tests/pages-smoke.js.
- Pendiente: probar HTTPS de Pages → Render → Supabase con dominios/configuración propios, aceptación de cookie __Host-, CSRF, recarga y logout/revocación. No se afirma éxito de cookies en producción.

## 2026-10-27 — Gastos compartidos
- Migración 0003 aplicada solo a PostgreSQL temporal de pruebas; SQL aditivo revisado offline. No se modifica producción ni splitly_dev.
- Backend: 87 pruebas aprobadas, pip check sin conflictos; Node: 14 pruebas aprobadas incluyendo dinero y regresión proxy.
- Capturas de implementación generadas en client/test-results/expenses-desktop.png, expenses-mobile.png y expenses-form.png, ignoradas por Git; se usan únicamente datos ficticios persistidos en tests.
- Pendiente publicar manualmente migración/backend/frontend y probar flujo completo en dominios HTTPS reales. No son evidencias de pagos ni de aceptación en producción.
- Frontend: lint/build finales aprobados y 15/15 pruebas de navegador; tres recorridos de gastos repetidos tras el ajuste visual del formulario. Capturas desktop 1440 px, móvil 390 px y formulario inspeccionadas; tabla de balances usa desplazamiento interno en móvil.
