import { useState } from 'react'
import './PasswordForm.css'


function PasswordChangeForm({
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = '',
  success = '',
}) {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    new_password_confirm: '',
  })

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const wasSuccessful = await onSubmit?.(
      formData
    )

    if (wasSuccessful) {
      setFormData({
        current_password: '',
        new_password: '',
        new_password_confirm: '',
      })
    }
  }

  return (
    <form
      className="password-form"
      onSubmit={handleSubmit}
    >
      <div className="password-form__field">
        <label htmlFor="current-password">
          Contraseña actual
        </label>

        <input
          id="current-password"
          name="current_password"
          type="password"
          value={formData.current_password}
          onChange={handleChange}
          autoComplete="current-password"
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="password-form__field">
        <label htmlFor="new-password">
          Nueva contraseña
        </label>

        <input
          id="new-password"
          name="new_password"
          type="password"
          value={formData.new_password}
          onChange={handleChange}
          autoComplete="new-password"
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="password-form__field">
        <label htmlFor="new-password-confirm">
          Confirmar nueva contraseña
        </label>

        <input
          id="new-password-confirm"
          name="new_password_confirm"
          type="password"
          value={formData.new_password_confirm}
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

      {success && (
        <div
          className="password-form__message password-form__message--success"
          role="status"
        >
          {success}
        </div>
      )}

      <div className="password-form__actions">
        {onCancel && (
          <button
            className="password-form__button password-form__button--secondary"
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </button>
        )}

        <button
          className="password-form__button password-form__button--primary"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? 'Actualizando...'
            : 'Cambiar contraseña'}
        </button>
      </div>
    </form>
  )
}

export default PasswordChangeForm