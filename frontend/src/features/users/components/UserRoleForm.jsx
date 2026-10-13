import { useState } from 'react'

const AVAILABLE_ROLES = [
  'ADMINISTRADOR',
  'DOCENTE',
  'PSICOLOGO',
  'TERAPEUTA',
  'RESPONSABLE_INSTITUCIONAL',
]

function UserRoleForm({
  user,
  onSubmit,
  onCancel,
}) {
  const [selectedRoles, setSelectedRoles] = useState(
    () => user.roles ?? []
  )

  function handleChange(event) {
    const { value, checked } = event.target

    setSelectedRoles((currentRoles) => {
      if (checked) {
        return [...currentRoles, value]
      }

      return currentRoles.filter(
        (role) => role !== value
      )
    })
  }

  function handleSubmit(event) {
    event.preventDefault()

    onSubmit?.(selectedRoles)
  }

  return (
    <form
      className="role-form"
      onSubmit={handleSubmit}
    >
      <p className="role-form__description">
        Selecciona los roles institucionales
        asignados a <strong>{user.username}</strong>.
      </p>

      <div className="role-options">
        {AVAILABLE_ROLES.map((role) => (
          <label
            className="role-option"
            key={role}
          >
            <input
              type="checkbox"
              value={role}
              checked={selectedRoles.includes(role)}
              onChange={handleChange}
            />

            <span>{role}</span>
          </label>
        ))}
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
          Guardar roles
        </button>
      </div>
    </form>
  )
}

export default UserRoleForm