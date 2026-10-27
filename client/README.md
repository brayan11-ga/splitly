# Frontend Splitly

Landing pública basada en `design/stitch/DESIGN.md` y la captura/HTML de la landing de Stitch.

```powershell
npm install
npm run dev
npm run build
npm run lint
```

- `/`: hero editorial, pasos, ejemplo ilustrativo en COP, beneficios y CTA.
- `/login` y `/register`: formularios reales con cookies HttpOnly y CSRF; usuarios autenticados pasan a dashboard.
- `/dashboard`: ruta protegida, nombre del usuario, listado real de grupos propios, estados vacío/error/carga y logout.
- Cualquier otra ruta: página de ruta no encontrada.
- React Router para navegación. En hosting estático, configurar fallback de rutas a `index.html` para las visitas directas (no reescribir peticiones de assets).
- Tailwind integrado con el plugin de Vite; tokens en `src/index.css`, composición editorial en `src/App.css`.
- Space Grotesk y Hanken Grotesk servidas localmente con Fontsource; sin CDN de fuentes ni scripts Stitch.
- Motion aparece una vez por sección. La preferencia de movimiento reducido desactiva las entradas y las transiciones CSS.
- El contenido financiero de la landing es un ejemplo fijo sin cálculos ni pagos. Autenticación y dashboard sí consultan el backend; la UI completa de gestión de grupos y gastos sigue pendiente.

## Revisión manual

Abrir a 1440, 1024, 768, 390 y 320 px; comparar jerarquía y espaciado con Stitch, verificar ausencia de scroll horizontal, navegación por teclado, foco, anclas, zoom al 200 %, preferencia de movimiento reducido y navegación atrás/adelante. Probar visitas directas a `/login` y `/register` en el hosting final. La compilación y lint no sustituyen estas comprobaciones.

## Interacciones de la landing

Sin dependencias nuevas. `PointerInteractions.jsx` contiene:

- `MagneticLink`: envolvente estable con 14 px de proximidad; el enlace se desplaza hasta ±6 px horizontal y ±4 px vertical con spring. Salir o enfocar devuelve el botón a su origen.
- `InteractiveCard`: pasos y beneficios se elevan 4 px, se desplazan hasta 2 px y rotan hasta 0,35 grados; un contorno de acento aparece sin cambiar dimensiones. Las tarjetas siguen siendo contenido, no controles falsos ni paradas extra de Tab.
- `HeroSurface`: el titular se mueve hasta 5/3 px y las líneas de fondo hasta 12/8 px en sentido opuesto. Mantiene la composición y la rotación original del fondo.
- `ContextLink`: indicador «Descubrir» solo sobre el enlace secundario del hero. Decorativo, aria-hidden, sin capturar clics y conservando el cursor del sistema.
- Navegación: subrayados, flechas direccionales, estados focus-visible y active en CSS.

`hooks/usePointerMotion.js` comparte la política de capacidades: solo ratón, `(hover: hover) and (pointer: fine)` y movimiento reducido desactivado. Usa Motion values/springs, no setState en pointermove, y eventos de puntero locales; los únicos suscriptores externos son cambios de media query con limpieza. No hay bucle global de animación ni listener global de mousemove. Al cambiar capacidades o activar movimiento reducido, los springs vuelven inmediatamente a cero.

### Probar en navegador

1. Acercar el ratón a ambos CTA principales, recorrer bordes y hacer clic: movimiento corto, vuelta natural y ruta `/register` correcta. Probar también clic central y Ctrl/cmd+clic.
2. Mover el puntero por esquinas de tarjetas, salir rápidamente y hacer scroll: elevación leve, texto legible, contornos y sin saltos del grid.
3. Recorrer el hero: titular y fondo reaccionan en sentidos opuestos; salir restaura su posición.
4. Pasar sobre «Descubre cómo funciona»: aparece el indicador; al salir, pulsar o enfocar desaparece. El enlace sigue saltando a la sección correspondiente.
5. Usar Tab/Shift+Tab y Enter: foco siempre visible, CTA estable al enfocar, sin paradas añadidas en tarjetas y navegación funcional.
6. Emular táctil y movimiento reducido (también cambiarlo con la página abierta): sin magnetismo, parallax, indicador ni transformaciones de hover; conservar estados de foco y active.
7. Revisar a 320, 390, 768 y 1440 px, zoom 200 %, sin desplazamiento horizontal ni solapamientos; comprobar rutas `/login`, `/register`, historial y anclas.
8. Opcional: React Profiler durante pointermove para confirmar que no se producen commits continuos; Performance para comprobar fluidez real en el dispositivo.

Build y lint verifican código y empaquetado; esta lista queda pendiente de revisión visual real.

## Autenticación y pruebas de integración

Configurar backend y aplicar manualmente 0002 según README raíz. `client/.env.example` propone VITE_API_URL vacío: Vite dirige /api a FastAPI 127.0.0.1:8000 y conserva el origen del navegador. Si se usa API absoluta, usar el mismo host local que el cliente, permitir su origen en CORS y configurar correctamente cookies. En hosting, VITE_API_URL se incorpora al compilar y no debe contener secretos. El proxy de Vite no existe en producción.

`services/api.js` envía credentials:include y X-CSRF-Token; `services/auth.js` restaura CSRF/usuario mediante me. AuthProvider no persiste secretos en el navegador y ProtectedRoute espera la comprobación antes de redirigir. Formularios accesibles con errores vinculados, confirmación de contraseña, botón mostrar/ocultar, loading y éxito al llegar al dashboard. Logout solo elimina el estado autenticado después de revocar la sesión o recibir 401.

Desde client, `npm test` ejecuta Playwright con React, FastAPI y PostgreSQL temporal real. Requiere dependencias backend, PostgreSQL local y permiso CREATEDB; inicia procesos exclusivos en 5175/8001 y NO usa splitly_dev como base de pruebas. En Windows usa Edge instalado; se puede elegir Chrome con PLAYWRIGHT_CHANNEL=chrome. En Linux/macOS instalar Chromium con `npx playwright install chromium`. La API auxiliar en server/tests incluye cierre solo para pruebas; esa ruta no existe en app.main. Si se interrumpe abruptamente, revisar restos de bases temporales.

Verificados seis flujos: rutas protegidas/landing, registro/cookie/recarga/logout revocado, login/error genérico, duplicado/confirmación, error de red y responsive/visibilidad de contraseña. Capturas de login desktop y registro a 390 px en test-results (ignorado), inspeccionadas visualmente. La suite respeta movimiento reducido; no reemplaza auditoría de accesibilidad ni pruebas del dominio HTTPS definitivo. Las interacciones originales de la landing siguen requiriendo la revisión manual descrita arriba.
