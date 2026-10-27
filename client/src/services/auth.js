import { apiRequest, setCsrfToken } from './api'

async function authenticate(path, body, signal) {
  const data = await apiRequest(path, { method: body ? 'POST' : 'GET', body, signal })
  setCsrfToken(data.csrf_token)
  return data.user
}

export const authService = {
  me: signal => authenticate('/auth/me', undefined, signal),
  login: values => authenticate('/auth/login', values),
  register: values => authenticate('/auth/register', values),
  async logout() {
    try { await apiRequest('/auth/logout', { method: 'POST' }) }
    catch (error) { if (error.status !== 401) throw error }
    setCsrfToken(null)
  },
}
