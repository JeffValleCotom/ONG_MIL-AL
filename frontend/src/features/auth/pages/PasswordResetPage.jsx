import { useEffect, useState } from 'react'

import {
  confirmPasswordRecovery,
  verifyPasswordRecovery,
} from '../services/authService'
import '../components/PasswordForm.css'
import './LoginPage.css'


function PasswordResetPage() {
  const [uid] = useState(
    () => new URLSearchParams(
      window.location.search
    ).get('uid') ?? ''
  )

  const [token] = useState(
    () => new URLSearchParams(
      window.location.search
    ).get('token') ?? ''
  )

  const [isVerifying, setIsVerifying] =
    useState(true)

  const [isValid, setIsValid] =
    useState(false)

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [error, setError] =
    useState('')

  const [success, setSuccess] =
    useState('')

  const [formData, setFormData] =
    useState({
      newPassword: '',
      newPasswordConfirm: '',
    })

  useEffect(() => {
    let isMounted = true

    async function verifyRecoveryLink() {
      if (!uid || !token) {
        if (isMounted) {
          setError(
            'El enlace de recuperación es inválido.'
          )
          setIsVerifying(false)
        }

        return
      }

      try {
        await verifyPasswordRecovery(
          uid,
          token
        )

        if (isMounted) {
          setIsValid(true)
        }
      } catch (verifyError) {
        if (isMounted) {
          setError(
            verifyError.message ||
              (
                'El enlace de recuperación '
                + 'es inválido o ha expirado.'
              )
          )
        }
      } finally {
        if (isMounted) {
          setIsVerifying(false)
        }
      }
    }

    verifyRecoveryLink()

    return () => {
      isMounted = false
    }
  }, [uid, token])

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setIsSubmitting(true)
    setError('')
    setSuccess('')

    try {
      const response =
        await confirmPasswordRecovery({
          uid,
          token,
          newPassword:
            formData.newPassword,
          newPasswordConfirm:
            formData.newPasswordConfirm,
        })

      setSuccess(
        response?.detail ||
          'Contraseña restablecida correctamente.'
      )

      setIsValid(false)

      setFormData({
        newPassword: '',
        newPasswordConfirm: '',
      })
    } catch (confirmError) {
      setError(
        confirmError.message ||
          'No fue posible restablecer la contraseña.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  function returnToLogin() {
    window.location.assign('/')
  }

  if (isVerifying) {
    return (
      <main className="login-page">
        <section className="login-card">
          <header className="login-card__header">
            <p className="login-card__eyebrow">
              ONG MIL-AL
            </p>

            <h1>Verificando enlace</h1>

            <p>
              Estamos comprobando que el enlace
              de recuperación sea válido.
            </p>
          </header>
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

          <h1>Restablecer contraseña</h1>

          <p>
            {isValid
              ? (
                'Ingresa una nueva contraseña '
                + 'para tu cuenta.'
              )
              : (
                'El proceso de recuperación '
                + 'no puede continuar.'
              )}
          </p>
        </header>

        {isValid && !success && (
          <form
            className="password-form"
            onSubmit={handleSubmit}
          >
            <div className="password-form__field">
              <label htmlFor="reset-new-password">
                Nueva contraseña
              </label>

              <input
                id="reset-new-password"
                name="newPassword"
                type="password"
                value={formData.newPassword}
                onChange={handleChange}
                autoComplete="new-password"
                required
                disabled={isSubmitting}
              />
            </div>

            <div className="password-form__field">
              <label htmlFor="reset-new-password-confirm">
                Confirmar nueva contraseña
              </label>

              <input
                id="reset-new-password-confirm"
                name="newPasswordConfirm"
                type="password"
                value={
                  formData.newPasswordConfirm
                }
                onChange={handleChange}
                autoComplete="new-password"
                required
                disabled={isSubmitting}
              />
            </div>

            {error && (
              <div
                className="password-form__message password-form__message--error"
                role="alert"
              >
                {error}
              </div>
            )}

            <div className="password-form__actions">
              <button
                className="password-form__button password-form__button--primary"
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? 'Restableciendo...'
                  : 'Restablecer contraseña'}
              </button>
            </div>
          </form>
        )}

        {!isValid && error && (
          <div
            className="password-form__message password-form__message--error"
            role="alert"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            className="password-form__message password-form__message--success"
            role="status"
          >
            {success}
          </div>
        )}

        {!isValid && (
          <button
            className="login-button"
            type="button"
            onClick={returnToLogin}
          >
            Volver al inicio de sesión
          </button>
        )}
      </section>
    </main>
  )
}

export default PasswordResetPage