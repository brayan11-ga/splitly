import { useEffect, useState } from 'react'

export default function useRemoteResource(load) {
  const [state, setState] = useState({ status: 'loading', data: null, error: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal).then(data => {
      if (!controller.signal.aborted) setState({ status: 'success', data, error: null })
    }).catch(error => {
      if (!controller.signal.aborted) setState({ status: 'error', data: null, error })
    })
    return () => controller.abort()
  }, [load, attempt])
  function reload() {
    setState(previous => ({ ...previous, status: 'loading', error: null }))
    setAttempt(previous => previous + 1)
  }
  function setData(update) {
    setState(previous => ({ status: 'success', data: typeof update === 'function' ? update(previous.data) : update, error: null }))
  }
  return { ...state, reload, setData }
}
