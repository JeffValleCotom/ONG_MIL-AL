import { useEffect, useState } from 'react'

import LoginForm from '../components/LoginForm'
import {
  changePassword,
  getSession,
  login,
  logout,
  requestPasswordRecovery,
} from '../services/authService'
import './LoginPage.css'
import PasswordRecoveryRequestForm
  from '../components/PasswordRecoveryRequestForm'
import PasswordChangeForm
  from '../components/PasswordChangeForm'

function LoginPage({
  onAuthenticated,
  onLoggedOut,
}) {

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [authenticatedUser, setAuthenticatedUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [isRecoveryMode, setIsRecoveryMode] =
    useState(false)
  const [recoveryMessage, setRecoveryMessage] =
    useState('')
  const [isPasswordChangeOpen, setIsPasswordChangeOpen] =
    useState(false)
  const [isChangingPassword, setIsChangingPassword] =
    useState(false)
  const [passwordChangeError, setPasswordChangeError] =
    useState('')
  const [passwordChangeSuccess, setPasswordChangeSuccess] =
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
        setAuthenticatedUser(session.user)
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

      setIsPasswordChangeOpen(false)
      setPasswordChangeError('')
      setPasswordChangeSuccess('')

      setAuthenticatedUser(session.user)
      onAuthenticated?.(session.user)

      setAuthenticatedUser(session.user)
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

function openPasswordChange() {
  setPasswordChangeError('')
  setPasswordChangeSuccess('')
  setIsPasswordChangeOpen(true)
}

function closePasswordChange() {
  setPasswordChangeError('')
  setPasswordChangeSuccess('')
  setIsPasswordChangeOpen(false)
}

async function handlePasswordChangeSubmit(
  passwordData
) {
  setIsChangingPassword(true)
  setPasswordChangeError('')
  setPasswordChangeSuccess('')

  try {
    const response = await changePassword(
      passwordData
    )

    setPasswordChangeSuccess(
      response?.detail ||
        'Contraseña actualizada correctamente.'
    )
    return true
  }

  catch (passwordError) {
    const validationMessage =
      passwordError.data?.current_password?.[0] ||
      passwordError.data?.new_password?.[0] ||
      passwordError.data?.new_password_confirm?.[0]

    setPasswordChangeError(
      validationMessage ||
        passwordError.message ||
        'No fue posible cambiar la contraseña.'
    )
    return true
  } finally {
    setIsChangingPassword(false)
  }
}
  async function handleLogout() {
  setIsLoggingOut(true)
  setError('')

  try {
    await logout()

    setIsPasswordChangeOpen(false)
    setPasswordChangeError('')
    setPasswordChangeSuccess('')

    setAuthenticatedUser(null)
    onLoggedOut?.()
  } catch (logoutError) {
    setError(
      logoutError.message ||
        'No fue posible cerrar la sesión.'
    )
    } finally {
      setIsLoggingOut(false)
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

          {error && (
            <div
              className="login-form__error"
              role="alert"
            >
              {error}
            </div>
          )}

          {!isPasswordChangeOpen && (
            <button
              className="login-button"
              type="button"
              onClick={openPasswordChange}
            >
              Cambiar contraseña
            </button>
          )}

          {isPasswordChangeOpen && (
            <PasswordChangeForm
              onSubmit={handlePasswordChangeSubmit}
              onCancel={closePasswordChange}
              isSubmitting={isChangingPassword}
              error={passwordChangeError}
              success={passwordChangeSuccess}
            />
          )}

          <button
            className="login-button"
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >

            {isLoggingOut
              ? 'Cerrando sesión...'
              : 'Cerrar sesión'}
          </button>
        </section>
      </main>
    )
  }
  if (isRecoveryMode) {
    return (
      <main className="login-page">
        <section className="login-card">
          <header className="login-card__header">
            <p className="login-card__eyebrow">
              ONG MIL-AL
            </p>

            <h1>Recuperar contraseña</h1>

            <p>
              Ingresa tu correo institucional.
              Si existe una cuenta asociada,
              recibirás instrucciones para continuar.
            </p>
          </header>

          <PasswordRecoveryRequestForm
            onSubmit={handleRecoverySubmit}
            onBack={closeRecovery}
            isSubmitting={isSubmitting}
            error={error}
            success={recoveryMessage}
          />
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

        <button
          className="login-link-button"
          type="button"
          onClick={openRecovery}
          disabled={isSubmitting}
        >
          ¿Olvidaste tu contraseña?
        </button>

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
