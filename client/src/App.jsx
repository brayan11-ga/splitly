import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { MotionConfig } from 'motion/react'
import { SiteHeader, SiteFooter } from './components/SiteLayout'
import LandingPage from './pages/LandingPage'
import PendingPage from './pages/PendingPage'
import AuthProvider from './auth/AuthProvider'
import ProtectedRoute from './auth/ProtectedRoute'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import './App.css'
export default function App() {
  return <MotionConfig reducedMotion="user"><BrowserRouter><AuthProvider><a className="skip-link" href="#contenido">Saltar al contenido</a><SiteHeader /><Routes><Route path="/" element={<LandingPage />} /><Route path="/login" element={<AuthPage key="login" kind="login" />} /><Route path="/register" element={<AuthPage key="register" kind="register" />} /><Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} /><Route path="*" element={<PendingPage kind="missing" />} /></Routes><SiteFooter /></AuthProvider></BrowserRouter></MotionConfig>
}
