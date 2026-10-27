import { useEffect, useRef, useSyncExternalStore } from 'react'
import { useReducedMotion, useSpring } from 'motion/react'

const query = '(hover: hover) and (pointer: fine)'
function subscribe(callback) {
  const media = window.matchMedia(query)
  media.addEventListener('change', callback)
  return () => media.removeEventListener('change', callback)
}
function getSnapshot() { return window.matchMedia(query).matches }
function getServerSnapshot() { return false }

// Spring values update styles directly, without React renders on pointermove.
export function usePointerEffectsEnabled() {
  const finePointer = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
  const reduced = useReducedMotion()
  return finePointer && reduced === false
}

export function usePointerMotion() {
  const enabled = usePointerEffectsEnabled()
  const bounds = useRef(null)
  const focused = useRef(false)
  const x = useSpring(0, { stiffness: 180, damping: 24, mass: 0.5 })
  const y = useSpring(0, { stiffness: 180, damping: 24, mass: 0.5 })
  const active = useSpring(0, { stiffness: 220, damping: 26 })

  useEffect(() => {
    if (!enabled) { x.jump(0); y.jump(0); active.jump(0) }
  }, [enabled, x, y, active])

  function reset() { x.set(0); y.set(0); active.set(0) }
  function move(event) {
    if (!enabled || event.pointerType !== 'mouse' || focused.current) return
    // Read the current rect so scrolling/resizing never leaves stale coordinates.
    const rect = bounds.current.getBoundingClientRect()
    x.set(Math.max(-1, Math.min(1, (event.clientX - rect.left) / rect.width * 2 - 1)))
    y.set(Math.max(-1, Math.min(1, (event.clientY - rect.top) / rect.height * 2 - 1)))
    active.set(1)
  }
  return {
    enabled, x, y, active, ref: bounds,
    handlers: {
      onPointerMove: move,
      onPointerLeave: reset,
      onPointerCancel: reset,
      onPointerDown: event => { if (event.pointerType !== 'mouse') reset() },
      onFocusCapture: () => { focused.current = true; reset() },
      onBlurCapture: () => { focused.current = false; reset() },
    },
  }
}
