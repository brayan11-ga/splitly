import { test, expect } from '@playwright/test'
import { randomUUID } from 'node:crypto'

const password = 'Una frase ficticia de pruebas 123'
const newEmail = () => `${randomUUID()}@example.com`

async function register(page, email = newEmail()) {
  await page.goto('/register')
  await page.getByLabel('Nombre completo', { exact: true }).fill('Persona Demo')
  await page.getByLabel('Correo electrónico', { exact: true }).fill(email)
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByLabel('Confirmar contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Crear mi cuenta', exact: true }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  await expect(page.getByRole('heading', { name: 'Hola, Persona Demo.' })).toBeVisible()
  return email
}

test('ruta protegida y landing disponibles', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/login$/)
  await expect(page.getByRole('heading', { name: 'Inicia sesión en tu cuenta' })).toBeVisible()
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('COMPARTE LOS PLANES.')
})

test('registro real, cookie HttpOnly, recarga y logout revocado', async ({ page, context }) => {
  await register(page)
  const cookie = (await context.cookies()).find(item => item.name === 'splitly_session')
  expect(cookie.httpOnly).toBeTruthy()
  expect(await page.evaluate(() => document.cookie)).not.toContain('splitly_session')
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([])
  expect(await page.evaluate(() => Object.keys(sessionStorage))).toEqual([])
  await expect(page.getByRole('heading', { name: 'El próximo plan empieza aquí.' })).toBeVisible()
  const identity = await (await page.request.get('http://127.0.0.1:8001/api/auth/me')).json()
  const group = await page.request.post('http://127.0.0.1:8001/api/groups', {
    headers: { Origin: 'http://127.0.0.1:5175', 'X-CSRF-Token': identity.csrf_token },
    data: { name: 'Plan de prueba persistente' },
  })
  expect(group.status()).toBe(201)
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Hola, Persona Demo.' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Plan de prueba persistente' })).toBeVisible()
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await expect(page).toHaveURL(/\/login$/)
  await context.addCookies([cookie])
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/login$/)
})

test('login correcto y contraseña incorrecta con error genérico', async ({ page }) => {
  const email = await register(page)
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await page.getByLabel('Correo electrónico', { exact: true }).fill(email)
  await page.getByLabel('Contraseña', { exact: true }).fill('incorrecta')
  await page.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
  await expect(page.getByRole('alert')).toHaveText('Correo o contraseña incorrectos.')
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  await expect(page.getByRole('heading', { name: 'Hola, Persona Demo.' })).toBeVisible()
})

test('registro duplicado y validación de confirmación', async ({ page }) => {
  const email = await register(page)
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await page.goto('/register')
  await page.getByLabel('Nombre completo', { exact: true }).fill('Otra Persona')
  await page.getByLabel('Correo electrónico', { exact: true }).fill(email)
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByLabel('Confirmar contraseña', { exact: true }).fill('no coincide')
  await page.getByRole('button', { name: 'Crear mi cuenta', exact: true }).click()
  await expect(page.getByText('Las contraseñas no coinciden.')).toBeVisible()
  await page.getByLabel('Confirmar contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Crear mi cuenta', exact: true }).click()
  await expect(page.getByRole('alert')).toHaveText('No pudimos registrar ese correo. Prueba iniciar sesión.')
})

test('error de red permite reintentar sin mostrar detalles técnicos', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Correo electrónico', { exact: true }).fill(newEmail())
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.route('**/api/auth/login', route => route.abort())
  await page.getByRole('button', { name: 'Iniciar sesión', exact: true }).click()
  await expect(page.getByRole('alert')).toHaveText('No pudimos conectar con Splitly. Inténtalo de nuevo.')
  await expect(page.getByRole('button', { name: 'Iniciar sesión', exact: true })).toBeEnabled()
})

test('formularios responsive y control de contraseña accesible', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/register')
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Mostrar contraseña', exact: true }).click()
  await expect(page.getByLabel('Contraseña', { exact: true })).toHaveAttribute('type', 'text')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
  await page.getByRole('button', { name: 'Ocultar contraseña', exact: true }).click()
  await page.getByLabel('Contraseña', { exact: true }).fill('')
  await page.screenshot({ path: testInfo.outputPath('register-mobile.png'), fullPage: true })
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Inicia sesión en tu cuenta' })).toBeVisible()
  await page.screenshot({ path: testInfo.outputPath('login-desktop.png'), fullPage: true })
})
