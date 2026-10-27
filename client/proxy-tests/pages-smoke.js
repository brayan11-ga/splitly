// Run with Pages dev on port 8788 and API_ORIGIN=http://invalid.example.
// Intentionally invalid config exercises the actual runtime without an upstream.
import assert from 'node:assert/strict'

const origin = 'http://127.0.0.1:8788'
for (const path of ['/', '/login', '/register', '/dashboard', '/groups', '/groups/example']) {
  const response = await fetch(`${origin}${path}`)
  assert.equal(response.status, 200, path)
  assert.match(response.headers.get('content-type'), /text\/html/, path)
  assert.match(await response.text(), /id="root"/, path)
}
for (const path of ['/api', '/api/health', '/api/auth/login', '/api/groups']) {
  const response = await fetch(`${origin}${path}`)
  assert.equal(response.status, 500, path)
  assert.match(response.headers.get('content-type'), /application\/json/, path)
  assert.equal(response.headers.get('cache-control'), 'no-store', path)
  assert.match((await response.json()).detail, /no está configurado/, path)
}
console.log('Pages runtime: 6 SPA routes and 4 API routes verified; no upstream requests.')
