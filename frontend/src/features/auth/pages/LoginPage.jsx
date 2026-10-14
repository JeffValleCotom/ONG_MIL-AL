import { useEffect, useState } from 'react'

import LoginForm from '../components/LoginForm'
import {
  getSession,
  login,
} from '../services/authService'
import './LoginPage.css'


function LoginPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [authenticatedUser, setAuthenticatedUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  useEffect(() => {
  let isMounted = true

  async function restoreSession() {
    try {
      const session = await getSession()

      if (
        isMounted &&
        session.authenticated &&
        session.user
      ) {
        setAuthenticatedUser(session.user)
      }
    } catch {
      if (isMounted) {
        setError(
          'No fue posible verificar la sesión actual.'
        )
      }
    } finally {
      if (isMounted) {
        setIsCheckingSession(false)
      }
    }
  }

  restoreSession()

  return () => {
    isMounted = false
  }
}, [])

  async function handleLoginSubmit(credentials) {
    setIsSubmitting(true)
    setError('')

    try {
      await login(credentials)

      const session = await getSession()

      if (!session.authenticated || !session.user) {
        throw new Error(
          'No fue posible confirmar la sesión autenticada.'
        )
      }

      setAuthenticatedUser(session.user)
    } catch (loginError) {
      setError(
        loginError.message ||
          'No fue posible iniciar sesión.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isCheckingSession) {
  return (
    <main className="login-page">
      <section className="login-card">
        <header className="login-card__header">
          <p className="login-card__eyebrow">
            ONG MIL-AL
          </p>

          <h1>Verificando sesión</h1>

          <p>
            Estamos comprobando tu sesión actual.
          </p>
        </header>
      </section>
    </main>
  )
}

  if (authenticatedUser) {
    return (
      <main className="login-page">
        <section className="login-card">
          <header className="login-card__header">
            <p className="login-card__eyebrow">
              ONG MIL-AL
            </p>

            <h1>Sesión activa</h1>

            <p>
              Usuario autenticado correctamente:
              {' '}
              <strong>
                {authenticatedUser.username}
              </strong>
            </p>
          </header>

          <p>
            La navegación posterior a la autenticación
            se implementará en las siguientes tareas.
          </p>
        </section>
      </main>
    )
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <header className="login-card__header">
          <p className="login-card__eyebrow">
            ONG MIL-AL
          </p>

          <h1>Iniciar sesión</h1>

          <p>
            Ingresa tus credenciales institucionales para acceder
            a la plataforma de seguimiento integral.
          </p>
        </header>

        <LoginForm
          onSubmit={handleLoginSubmit}
          isSubmitting={isSubmitting}
          error={error}
        />

        <footer className="login-card__footer">
          <p>
            El acceso está disponible únicamente para usuarios
            autorizados de MIL-AL.
          </p>
        </footer>
      </section>
    </main>
  )
}

export default LoginPage