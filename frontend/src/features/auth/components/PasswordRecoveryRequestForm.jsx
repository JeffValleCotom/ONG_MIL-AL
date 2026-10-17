import { useState } from 'react'


function PasswordRecoveryRequestForm({
  onSubmit,
  onBack,
  isSubmitting = false,
  error = '',
  success = '',
}) {
  const [email, setEmail] = useState('')

  function handleSubmit(event) {
    event.preventDefault()

    onSubmit?.(email)
  }

  return (
    <form
      className="login-form"
      onSubmit={handleSubmit}
    >
      <div className="form-field">
        <label htmlFor="recovery-email">
          Correo electrónico
        </label>

        <input
          id="recovery-email"
          name="email"
          type="email"
          value={email}
          onChange={(event) =>
            setEmail(event.target.value)
          }
          autoComplete="email"
          required
          disabled={isSubmitting}
        />
      </div>

      {error && (
        <div
          className="login-form__error"
          role="alert"
        >
          {error}
        </div>
      )}

      {success && (
        <div
          className="login-form__success"
          role="status"
        >
          {success}
        </div>
      )}

      <button
        className="login-button"
        type="submit"
        disabled={isSubmitting}
      >
        {isSubmitting
          ? 'Enviando...'
          : 'Enviar instrucciones'}
      </button>

      <button
        className="login-link-button"
        type="button"
        onClick={onBack}
        disabled={isSubmitting}
      >
        Volver al inicio de sesión
      </button>
    </form>
  )
}

export default PasswordRecoveryRequestForm