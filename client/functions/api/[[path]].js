// Runtime-only binding: never read API_ORIGIN from import.meta.env or VITE_*.
const HOP_BY_HOP = [
  'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
  'te', 'trailer', 'transfer-encoding', 'upgrade',
]

function stripHopByHop(headers) {
  const connectionTokens = (headers.get('connection') || '').split(',')
  for (const name of connectionTokens) {
    if (name.trim()) headers.delete(name.trim())
  }
  for (const name of HOP_BY_HOP) headers.delete(name)
}

function failure(status, detail) {
  return Response.json({ detail }, {
    status, headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' },
  })
}

export async function onRequest({ request, env }) {
  const incoming = new URL(request.url)
  if (incoming.pathname !== '/api' && !incoming.pathname.startsWith('/api/')) {
    return failure(404, 'Ruta de API no encontrada.')
  }

  let target
  try {
    target = new URL(env.API_ORIGIN)
    if (target.protocol !== 'https:' || target.username || target.password ||
        target.pathname !== '/' || target.search || target.hash || target.origin === incoming.origin) {
      throw new Error('Invalid API origin')
    }
  } catch {
    return failure(500, 'El proxy de API no está configurado correctamente.')
  }

  // Assign pathname rather than resolving a user-controlled URL against a base.
  // Neither query parameters, headers nor route params can select another host.
  target.pathname = incoming.pathname
  target.search = incoming.search
  const headers = new Headers(request.headers)
  stripHopByHop(headers)
  for (const name of [...headers.keys()]) {
    if (name === 'host' || name === 'forwarded' || name.startsWith('x-forwarded-')) headers.delete(name)
  }
  headers.set('X-Forwarded-Host', incoming.host)
  headers.set('X-Forwarded-Proto', incoming.protocol.slice(0, -1))
  // Origin, Referer, Cookie and X-CSRF-Token remain exactly as received.
  // In particular, never manufacture a trusted Origin for absent/hostile origins.
  headers.delete('content-length')
  const outbound = new Request(new Request(target, request), {
    headers, redirect: 'manual', cache: 'no-store',
  })

  try {
    const upstream = await fetch(outbound)
    // Copy Headers as a collection: never join/split Set-Cookie on commas
    // (Expires contains commas). Preserve all cookies, including logout expiry.
    const responseHeaders = new Headers(upstream.headers)
    stripHopByHop(responseHeaders)
    responseHeaders.set('Cache-Control', 'no-store')
    responseHeaders.set('X-Content-Type-Options', 'nosniff')
    const location = responseHeaders.get('location')
    if (location && upstream.status >= 300 && upstream.status < 400) {
      const redirect = new URL(location, target)
      if (redirect.host !== target.host || !['https:', 'http:'].includes(redirect.protocol) ||
          redirect.username || redirect.password ||
          (redirect.pathname !== '/api' && !redirect.pathname.startsWith('/api/'))) {
        return failure(502, 'La API devolvió una redirección no permitida.')
      }
      // Keep FastAPI slash redirects same-origin, including method-preserving 307s.
      redirect.protocol = incoming.protocol
      redirect.host = incoming.host
      responseHeaders.set('Location', redirect.href)
    }
    return new Response(upstream.body, {
      status: upstream.status, statusText: upstream.statusText, headers: responseHeaders,
    })
  } catch {
    // No upstream URLs, credentials, bodies or cookies in errors/logs.
    return failure(502, 'No se pudo conectar con la API. Inténtalo de nuevo.')
  }
}
