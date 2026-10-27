# Frontend Splitly

Landing pública basada en `design/stitch/DESIGN.md` y la captura/HTML de la landing de Stitch.

```powershell
npm install
npm run dev
npm run build
npm run lint
```

- `/`: hero editorial, pasos, ejemplo ilustrativo en COP, beneficios y CTA.
- `/login` y `/register`: páginas provisionales; no reciben datos ni autentican.
- Cualquier otra ruta: página de ruta no encontrada.
- React Router para navegación. En hosting estático, configurar fallback de rutas a `index.html` para las visitas directas (no reescribir peticiones de assets).
- Tailwind integrado con el plugin de Vite; tokens en `src/index.css`, composición editorial en `src/App.css`.
- Space Grotesk y Hanken Grotesk servidas localmente con Fontsource; sin CDN de fuentes ni scripts Stitch.
- Motion aparece una vez por sección. La preferencia de movimiento reducido desactiva las entradas y las transiciones CSS.
- El contenido financiero es un ejemplo fijo; no implementa cálculos ni persistencia, no se conecta al backend y no simula pagos exitosos.

## Revisión manual

Abrir a 1440, 1024, 768, 390 y 320 px; comparar jerarquía y espaciado con Stitch, verificar ausencia de scroll horizontal, navegación por teclado, foco, anclas, zoom al 200 %, preferencia de movimiento reducido y navegación atrás/adelante. Probar visitas directas a `/login` y `/register` en el hosting final. La compilación y lint no sustituyen estas comprobaciones.
