import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { MotionConfig } from 'motion/react'
import { SiteHeader, SiteFooter } from './components/SiteLayout'
import LandingPage from './pages/LandingPage'
import PendingPage from './pages/PendingPage'
import './App.css'
export default function App() {
  return <MotionConfig reducedMotion="user"><BrowserRouter><a className="skip-link" href="#contenido">Saltar al contenido</a><SiteHeader /><Routes><Route path="/" element={<LandingPage />} /><Route path="/login" element={<PendingPage kind="login" />} /><Route path="/register" element={<PendingPage kind="register" />} /><Route path="*" element={<PendingPage kind="missing" />} /></Routes><SiteFooter /></BrowserRouter></MotionConfig>
}
