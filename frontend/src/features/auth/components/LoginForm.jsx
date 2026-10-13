import { useState } from 'react'

function LoginForm({
  onSubmit,
  isSubmitting = false,
  error = '',
}) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()

    onSubmit?.(formData)
  }

  return (
    <form
      className="login-form"
      onSubmit={handleSubmit}
    >
      <div className="form-field">
        <label htmlFor="login-username">
          Usuario
        </label>

        <input
          id="login-username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          autoComplete="username"
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="login-password">
          Contraseña
        </label>

        <input
          id="login-password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          autoComplete="current-password"
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

      <button
        className="login-button"
        type="submit"
        disabled={isSubmitting}
      >
        {isSubmitting
          ? 'Iniciando sesión...'
          : 'Iniciar sesión'}
      </button>
    </form>
  )
}

export default LoginForm