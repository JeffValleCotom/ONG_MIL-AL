import { useEffect, useState } from 'react'

import AuthLayout
  from '../../../components/auth/AuthLayout'
import LoginForm from '../components/LoginForm'
import {
  getSession,
  login,
  requestPasswordRecovery,
} from '../services/authService'
import './LoginPage.css'
import PasswordRecoveryRequestForm
  from '../components/PasswordRecoveryRequestForm'

function LoginPage({
  onAuthenticated,
}) {

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  const [isRecoveryMode, setIsRecoveryMode] =
    useState(false)

  const [recoveryMessage, setRecoveryMessage] =
    useState('')

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
        onAuthenticated?.(session.user)
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
}, [onAuthenticated])

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

      onAuthenticated?.(session.user)
    } catch (loginError) {
      setError(
        loginError.message ||
          'No fue posible iniciar sesión.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleRecoverySubmit(email) {
  setIsSubmitting(true)
  setError('')
  setRecoveryMessage('')

  try {
    const response = await requestPasswordRecovery(
      email
    )

    setRecoveryMessage(
      response?.detail ||
        (
          'Si existe una cuenta asociada, '
          + 'se enviarán instrucciones de recuperación.'
        )
    )
  } catch (recoveryError) {
    setError(
      recoveryError.message ||
        'No fue posible procesar la solicitud.'
    )
  } finally {
    setIsSubmitting(false)
  }
}

function openRecovery() {
  setError('')
  setRecoveryMessage('')
  setIsRecoveryMode(true)
}

function closeRecovery() {
  setError('')
  setRecoveryMessage('')
  setIsRecoveryMode(false)
}

  if (isCheckingSession) {
    return (
      <AuthLayout
        eyebrow="Acceso institucional"
        title="Verificando sesión"
        description={
          'Estamos comprobando tu sesión actual.'
        }
      >
        <p className="milal-auth__notice">
          Esto tomará solo un momento.
        </p>
      </AuthLayout>
    )
  }

  if (isRecoveryMode) {
    return (
      <AuthLayout
        eyebrow="Recuperación de acceso"
        title="Recuperar contraseña"
        description={
          'Ingresa tu correo institucional. '
          + 'Si existe una cuenta asociada, '
          + 'recibirás instrucciones para continuar.'
        }
      >
        <PasswordRecoveryRequestForm
          onSubmit={handleRecoverySubmit}
          onBack={closeRecovery}
          isSubmitting={isSubmitting}
          error={error}
          success={recoveryMessage}
        />
      </AuthLayout>
    )
  }
  return (
    <AuthLayout
      eyebrow="Acceso institucional"
      title="Iniciar sesión"
      description={
        'Ingresa tus credenciales institucionales '
        + 'para acceder a la plataforma.'
      }
    >
      <LoginForm
        onSubmit={handleLoginSubmit}
        isSubmitting={isSubmitting}
        error={error}
      />

      <button
        className="login-link-button"
        type="button"
        onClick={openRecovery}
        disabled={isSubmitting}
      >
        ¿Olvidaste tu contraseña?
      </button>

      <p className="milal-auth__notice">
        El acceso está disponible únicamente para
        usuarios autorizados de MIL-AL.
      </p>
    </AuthLayout>
  )
}

export default LoginPage
