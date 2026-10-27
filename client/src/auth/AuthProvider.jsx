import { useEffect, useState } from 'react'
import { AuthContext } from './AuthContext'
import { authService } from '../services/auth'
import { onUnauthorized } from '../services/api'

export default function AuthProvider({ children }) {
  const [state, setState] = useState({ status: 'loading', user: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    authService.me(controller.signal).then(user => {
      if (!controller.signal.aborted) setState({ status: 'authenticated', user })
    }).catch(error => {
      if (!controller.signal.aborted) setState({ status: error.status === 401 ? 'anonymous' : 'error', user: null })
    })
    return () => controller.abort()
  }, [attempt])
  useEffect(() => onUnauthorized(() => setState({ status: 'anonymous', user: null })), [])
  async function authenticate(kind, values) {
    const user = await authService[kind](values)
    setState({ status: 'authenticated', user })
  }
  async function logout() {
    await authService.logout()
    setState({ status: 'anonymous', user: null })
  }
  function retry() { setState({ status: 'loading', user: null }); setAttempt(previous => previous + 1) }
  return <AuthContext.Provider value={{ ...state, refresh: retry, authenticate, logout }}>{children}</AuthContext.Provider>
}
