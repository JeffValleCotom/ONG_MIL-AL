import { useState } from 'react'

function getInitialFormData(user) {
  if (!user) {
    return {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
    }
  }

  return {
    username: user.username ?? '',
    email: user.email ?? '',
    first_name: user.first_name ?? '',
    last_name: user.last_name ?? '',
    password: '',
  }
}

function UserForm({
  user = null,
  onSubmit,
  onCancel,
}) {
  const isEditing = Boolean(user)

  const [formData, setFormData] = useState(
    () => getInitialFormData(user)
  )

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
      className="user-form"
      onSubmit={handleSubmit}
    >
      <div className="form-field">
        <label htmlFor="username">
          Usuario
        </label>

        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          required
          autoComplete="username"
        />
      </div>

      <div className="form-field">
        <label htmlFor="email">
          Correo electrónico
        </label>

        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          autoComplete="email"
        />
      </div>

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="first_name">
            Nombres
          </label>

          <input
            id="first_name"
            name="first_name"
            type="text"
            value={formData.first_name}
            onChange={handleChange}
            autoComplete="given-name"
          />
        </div>

        <div className="form-field">
          <label htmlFor="last_name">
            Apellidos
          </label>

          <input
            id="last_name"
            name="last_name"
            type="text"
            value={formData.last_name}
            onChange={handleChange}
            autoComplete="family-name"
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="password">
          {isEditing
            ? 'Nueva contraseña'
            : 'Contraseña'}
        </label>

        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          required={!isEditing}
          autoComplete="new-password"
        />

        {isEditing && (
          <small>
            Déjala vacía para conservar la contraseña actual.
          </small>
        )}
      </div>

      <div className="form-actions">
        <button
          className="button button--secondary"
          type="button"
          onClick={onCancel}
        >
          Cancelar
        </button>

        <button
          className="button button--primary"
          type="submit"
        >
          {isEditing
            ? 'Guardar cambios'
            : 'Registrar usuario'}
        </button>
      </div>
    </form>
  )
}

export default UserForm