import { motion, useMotionValue, useTransform } from 'motion/react'
import { Link } from 'react-router-dom'
import { useReducedMotion } from 'motion/react'
import { usePointerEffectsEnabled, usePointerMotion } from '../hooks/usePointerMotion'

const MotionLink = motion.create(Link)

export function MagneticLink({ children, to, className }) {
  const { ref, handlers, x, y, enabled } = usePointerMotion()
  const translateX = useTransform(x, [-1, 1], [-6, 6])
  const translateY = useTransform(y, [-1, 1], [-4, 4])
  return (
    <span className="magnetic-zone" ref={ref} {...handlers}>
      <MotionLink to={to} className={className}
        style={{ x: translateX, y: translateY }}
        whileTap={enabled ? { scale: 0.985 } : undefined}>
        {children}
      </MotionLink>
    </span>
  )
}

export function InteractiveCard({ children, className = '' }) {
  const reduced = useReducedMotion()
  const { ref, handlers, x, y, active } = usePointerMotion()
  const translateX = useTransform(x, [-1, 1], [-2, 2])
  const translateY = useTransform(active, [0, 1], [0, -4])
  const rotate = useTransform(y, [-1, 1], [-0.35, 0.35])
  return (
    <motion.article ref={ref} {...handlers}
      className={`interactive-card ${className}`}
      initial={reduced ? false : { opacity: 0 }}
      whileInView={{ opacity: 1 }} viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: reduced ? 0 : 0.45 }}
      style={{ x: translateX, y: translateY, rotate }}>
      {children}
    </motion.article>
  )
}

export function HeroSurface({ children }) {
  const { ref, handlers, x, y } = usePointerMotion()
  const titleX = useTransform(x, [-1, 1], [-5, 5])
  const titleY = useTransform(y, [-1, 1], [-3, 3])
  const backdropX = useTransform(x, [-1, 1], [12, -12])
  const backdropY = useTransform(y, [-1, 1], [8, -8])
  return (
    <motion.section ref={ref} {...handlers} className="hero-section"
      style={{ '--title-x': titleX, '--title-y': titleY, '--backdrop-x': backdropX, '--backdrop-y': backdropY }}>
      {children}
    </motion.section>
  )
}

// A decorative cue on a real anchor; the system cursor remains visible.
export function ContextLink({ children, href, className, label = 'Descubrir' }) {
  const enabled = usePointerEffectsEnabled()
  const cursorX = useMotionValue(0)
  const cursorY = useMotionValue(0)
  const opacity = useMotionValue(0)
  function hide() { opacity.set(0) }
  function move(event) {
    if (!enabled || event.pointerType !== 'mouse' || event.currentTarget.matches(':focus-visible')) {
      hide()
      return
    }
    const rect = event.currentTarget.getBoundingClientRect()
    cursorX.set(Math.max(0, Math.min(rect.width - 100, event.clientX - rect.left + 16)))
    cursorY.set(event.clientY - rect.top - 36)
    opacity.set(1)
  }
  return (
    <a href={href} className={`context-link ${className}`}
      onPointerMove={move} onPointerLeave={hide} onPointerCancel={hide}
      onPointerDown={hide} onWheel={hide} onFocus={hide} onBlur={hide}>
      {children}
      <motion.span aria-hidden="true" className="context-indicator eyebrow"
        style={{ x: cursorX, y: cursorY, opacity: enabled ? opacity : 0 }}>
        {label} ↗
      </motion.span>
    </a>
  )
}
