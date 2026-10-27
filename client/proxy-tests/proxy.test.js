import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'
import { onRequest } from '../functions/api/[[path]].js'
import { onRequest as exactApiRoute } from '../functions/api.js'

const frontend = 'https://splitly.example'
const env = { API_ORIGIN: 'https://splitly-api.onrender.com' }
const session = '__Host-splitly_session=fictitious; HttpOnly; Secure; SameSite=lax; Path=/'
const call = (request, bindings = env) => onRequest({ request, env: bindings })

test('methods, raw bodies, queries and authentication headers reach only configured Render', async t => {
  for (const method of ['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']) {
    const body = ['GET', 'HEAD'].includes(method) ? undefined : '{"name":"Viaje Bogotá"}'
    t.mock.method(globalThis, 'fetch', async request => {
      const target = new URL(request.url)
      assert.equal(target.origin, env.API_ORIGIN)
      assert.equal(target.pathname, '/api/groups')
      assert.equal(target.search, '?name=Ana%20Maria&target=https://hostile.example&x=1&x=2')
      assert.equal(request.method, method)
      assert.equal(await request.text(), body || '')
      assert.equal(request.headers.get('host'), null)
      assert.equal(request.headers.get('cookie'), '__Host-splitly_session=fictitious')
      assert.equal(request.headers.get('origin'), frontend)
      assert.equal(request.headers.get('referer'), `${frontend}/groups`)
      assert.equal(request.headers.get('x-csrf-token'), 'test-csrf')
      assert.equal(request.headers.get('x-forwarded-host'), 'splitly.example')
      assert.equal(request.headers.get('x-forwarded-proto'), 'https')
      assert.equal(request.headers.get('forwarded'), null)
      assert.equal(request.headers.get('connection'), null)
      assert.equal(request.headers.get('x-hop'), null)
      assert.equal(request.redirect, 'manual')
      assert.equal(request.cache, 'no-store')
      return new Response(null, { status: 204 })
    })
    const result = await call(new Request(`${frontend}/api/groups?name=Ana%20Maria&target=https://hostile.example&x=1&x=2`, {
      method, body,
      headers: {
        'Content-Type': 'application/json', Cookie: '__Host-splitly_session=fictitious',
        Origin: frontend, Referer: `${frontend}/groups`, 'X-CSRF-Token': 'test-csrf',
        Host: 'hostile.example', Forwarded: 'host=hostile.example',
        'X-Forwarded-Host': 'hostile.example', 'X-Forwarded-Proto': 'http',
        Connection: 'X-Hop', 'X-Hop': 'remove-me',
      },
    }))
    assert.equal(result.status, 204)
    assert.equal(await result.text(), '')
    t.mock.restoreAll()
  }
})

test('Origin and CSRF are never invented, normalized or elevated', async t => {
  for (const origin of [undefined, 'null', 'https://hostile.example']) {
    t.mock.method(globalThis, 'fetch', request => {
      assert.equal(request.headers.get('origin'), origin ?? null)
      assert.equal(request.headers.get('x-csrf-token'), null)
      return Response.json({ detail: 'CSRF rechazado' }, { status: 403 })
    })
    const response = await call(new Request(`${frontend}/api/groups`, {
      method: 'POST', headers: origin ? { Origin: origin } : {},
    }))
    assert.equal(response.status, 403)
    t.mock.restoreAll()
  }
})

test('multiple Set-Cookie headers including Expires survive without attribute rewrites', async t => {
  const headers = new Headers({ 'Cache-Control': 'public, max-age=3600' })
  headers.append('Set-Cookie', session)
  headers.append('Set-Cookie', 'extra=fictitious; Expires=Wed, 21 Oct 2037 07:28:00 GMT; Path=/; Secure; HttpOnly; SameSite=Strict')
  t.mock.method(globalThis, 'fetch', () => new Response('{"csrf_token":"test"}', { status: 201, headers }))
  const response = await call(new Request(`${frontend}/api/auth/register`, { method: 'POST' }))
  assert.deepEqual(response.headers.getSetCookie(), headers.getSetCookie())
  assert.equal(response.headers.get('cache-control'), 'no-store')
  assert.equal(response.status, 201)
  assert.deepEqual(await response.json(), { csrf_token: 'test' })
})

test('logout deletion cookie and empty 204 survive', async t => {
  const deletion = '__Host-splitly_session=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; Path=/; SameSite=lax; Secure; HttpOnly'
  t.mock.method(globalThis, 'fetch', () => new Response(null, { status: 204, headers: { 'Set-Cookie': deletion } }))
  const response = await call(new Request(`${frontend}/api/auth/logout`, { method: 'POST' }))
  assert.equal(response.status, 204)
  assert.deepEqual(response.headers.getSetCookie(), [deletion])
  assert.equal(await response.text(), '')
})

test('error statuses and JSON are passed through without caching', async t => {
  for (const status of [401, 403, 404, 409, 422, 429, 500, 503]) {
    t.mock.method(globalThis, 'fetch', () => Response.json({ detail: 'backend' }, { status }))
    const response = await call(new Request(`${frontend}/api/groups`))
    assert.equal(response.status, status)
    assert.deepEqual(await response.json(), { detail: 'backend' })
    assert.equal(response.headers.get('cache-control'), 'no-store')
    t.mock.restoreAll()
  }
})

test('FastAPI relative and absolute slash redirects stay on Pages with status 307', async t => {
  for (const location of ['/api/groups/?x=1', 'https://splitly-api.onrender.com/api/groups/?x=1', 'http://splitly-api.onrender.com/api/groups/?x=1']) {
    t.mock.method(globalThis, 'fetch', () => new Response(null, { status: 307, headers: { Location: location, 'Set-Cookie': session } }))
    const response = await call(new Request(`${frontend}/api/groups`, { method: 'POST' }))
    assert.equal(response.status, 307)
    assert.equal(response.headers.get('location'), `${frontend}/api/groups/?x=1`)
    assert.deepEqual(response.headers.getSetCookie(), [session])
    t.mock.restoreAll()
  }
})

test('external or non-API redirects are blocked instead of following with credentials', async t => {
  for (const location of ['https://hostile.example/api/groups', '//hostile.example/api/auth/me', '/docs', 'https://user:pass@splitly-api.onrender.com/api/groups']) {
    t.mock.method(globalThis, 'fetch', () => new Response(null, { status: 307, headers: { Location: location } }))
    const response = await call(new Request(`${frontend}/api/groups`))
    assert.equal(response.status, 502)
    assert.equal(response.headers.get('location'), null)
    t.mock.restoreAll()
  }
})

test('invalid config fails closed without any network calls', async t => {
  const mock = t.mock.method(globalThis, 'fetch', () => { throw new Error('must not fetch') })
  for (const origin of [undefined, '', 'http://api.example', 'https://user:pass@api.example', 'https://api.example/api', 'https://api.example?target=x', 'https://api.example#x', frontend]) {
    const response = await call(new Request(`${frontend}/api/health`), { API_ORIGIN: origin })
    assert.equal(response.status, 500)
  }
  assert.equal(mock.mock.callCount(), 0)
})

test('network failures return generic 502 without sensitive upstream details', async t => {
  t.mock.method(globalThis, 'fetch', () => { throw new Error('private-cookie-and-upstream-data') })
  const response = await call(new Request(`${frontend}/api/health`))
  assert.equal(response.status, 502)
  assert.doesNotMatch(await response.text(), /private-cookie|onrender/)
})

test('path resembling a URL cannot change the upstream host', async t => {
  t.mock.method(globalThis, 'fetch', request => {
    assert.equal(new URL(request.url).origin, env.API_ORIGIN)
    assert.equal(new URL(request.url).pathname, '/api//hostile.example/path')
    return new Response(null, { status: 404 })
  })
  assert.equal((await call(new Request(`${frontend}/api//hostile.example/path`))).status, 404)
})

test('exact /api is proxied and non-API routes cannot be intercepted by the handler', async t => {
  assert.equal(exactApiRoute, onRequest)
  const mock = t.mock.method(globalThis, 'fetch', request => {
    assert.equal(new URL(request.url).pathname, '/api')
    return new Response(null, { status: 404 })
  })
  assert.equal((await exactApiRoute({ request: new Request(`${frontend}/api`), env })).status, 404)
  for (const path of ['/login', '/register', '/dashboard', '/groups/123', '/assets/test.js', '/api-other']) {
    assert.equal((await call(new Request(`${frontend}${path}`))).status, 404)
  }
  assert.equal(mock.mock.callCount(), 1)
})

test('Pages routing only invokes API functions; SPA assets and local Vite proxy stay intact', async () => {
  const routes = JSON.parse(await readFile(new URL('../public/_routes.json', import.meta.url), 'utf8'))
  assert.deepEqual(routes, { version: 1, include: ['/api', '/api/*'], exclude: [] })
  const vite = await readFile(new URL('../vite.config.js', import.meta.url), 'utf8')
  assert.match(vite, /target: 'http:\/\/127\.0\.0\.1:8000'/)
  const client = await readFile(new URL('../src/services/api.js', import.meta.url), 'utf8')
  assert.match(client, /credentials: 'include'/)
  assert.match(client, /X-CSRF-Token/)
})
