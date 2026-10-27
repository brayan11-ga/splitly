import { motion, useReducedMotion } from 'motion/react'
import { Link } from 'react-router-dom'
const MotionLink = motion.create(Link)
export function Arrow({ down = false }) {
  return <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" style={down ? { transform: 'rotate(90deg)' } : undefined}><path d="M4 12h15M13 5l7 7-7 7" /></svg>
}
export function Reveal({ children, className = '', delay = 0 }) {
  const reduced = useReducedMotion()
  return <motion.div className={className} initial={reduced ? false : { opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.12 }} transition={{ duration: reduced ? 0 : 0.5, delay: reduced ? 0 : delay }}>{children}</motion.div>
}
export function ActionLink({ children, to = '/register' }) {
  const reduced = useReducedMotion()
  return <MotionLink className="action action-primary" to={to} whileHover={reduced ? undefined : { y: -2 }} whileTap={reduced ? undefined : { scale: 0.98 }} transition={{ duration: 0.15 }}>{children}<Arrow /></MotionLink>
}
export function SectionHeading({ label, children, aside }) {
  return <div className="section-heading"><div><p className="eyebrow text-lime">{label}</p><h2>{children}</h2></div>{aside && <p className="section-aside">{aside}</p>}</div>
}
