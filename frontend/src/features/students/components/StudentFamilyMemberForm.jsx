import { useState } from 'react'

const RELATIONSHIP_OPTIONS = [
  {
    value: 'MADRE',
    label: 'Madre',
  },
  {
    value: 'PADRE',
    label: 'Padre',
  },
  {
    value: 'HERMANO_A',
    label: 'Hermano/a',
  },
  {
    value: 'ABUELO_A',
    label: 'Abuelo/a',
  },
  {
    value: 'TIO_A',
    label: 'Tío/a',
  },
  {
    value: 'TUTOR',
    label: 'Tutor',
  },
  {
    value: 'CUIDADOR',
    label: 'Cuidador',
  },
  {
    value: 'OTRO',
    label: 'Otro',
  },
]

function StudentFamilyMemberForm({
  initialData = null,
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = '',
  success = '',
}) {

  const [formData, setFormData] = useState({
    first_name: initialData?.first_name ?? '',
    last_name: initialData?.last_name ?? '',
    relationship: initialData?.relationship ?? '',
    relationship_detail:
      initialData?.relationship_detail ?? '',
    phone: initialData?.phone ?? '',
    email: initialData?.email ?? '',
    address: initialData?.address ?? '',
    is_primary_contact:
      initialData?.is_primary_contact ?? false,
  })

  const [validationError, setValidationError] =
    useState('')

  const isEditing = Boolean(initialData)

  function handleChange(event) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target

    setFormData((current) => {
      const nextValue = (
        type === 'checkbox'
          ? checked
          : value
      )

      const nextData = {
        ...current,
        [name]: nextValue,
      }

      if (
        name === 'relationship'
        && value !== 'OTRO'
      ) {
        nextData.relationship_detail = ''
      }

      return nextData
    })
  }

  function handleSubmit(event) {
    event.preventDefault()
    setValidationError('')

    const familyMemberData = {
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      relationship: formData.relationship,
      relationship_detail:
        formData.relationship_detail.trim(),
      phone: formData.phone.trim(),
      email: formData.email.trim(),
      address: formData.address.trim(),
      is_primary_contact:
        formData.is_primary_contact,
    }

    if (
      !familyMemberData.first_name
      || !familyMemberData.last_name
      || !familyMemberData.relationship
    ) {
      setValidationError(
        'Completa todos los campos obligatorios.'
      )
      return
    }

    if (
      familyMemberData.relationship === 'OTRO'
      && !familyMemberData.relationship_detail
    ) {
      setValidationError(
        'Especifica el parentesco cuando selecciones Otro.'
      )
      return
    }

    onSubmit?.(familyMemberData)
  }

  return (
    <form
      className="student-form"
      onSubmit={handleSubmit}
    >
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="family_first_name">
            Nombres
          </label>

          <input
            id="family_first_name"
            name="first_name"
            type="text"
            maxLength="100"
            value={formData.first_name}
            onChange={handleChange}
            required
            autoComplete="given-name"
            disabled={isSubmitting}
          />
        </div>

        <div className="form-field">
          <label htmlFor="family_last_name">
            Apellidos
          </label>

          <input
            id="family_last_name"
            name="last_name"
            type="text"
            maxLength="100"
            value={formData.last_name}
            onChange={handleChange}
            required
            autoComplete="family-name"
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="family_relationship">
            Parentesco
          </label>

          <select
            id="family_relationship"
            name="relationship"
            value={formData.relationship}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          >
            <option value="">
              Selecciona un parentesco
            </option>

            {RELATIONSHIP_OPTIONS.map(
              (option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              )
            )}
          </select>
        </div>

        {formData.relationship === 'OTRO' && (
          <div className="form-field">
            <label htmlFor="family_relationship_detail">
              Especifique el parentesco
            </label>

            <input
              id="family_relationship_detail"
              name="relationship_detail"
              type="text"
              maxLength="100"
              value={
                formData.relationship_detail
              }
              onChange={handleChange}
              required
              disabled={isSubmitting}
            />
          </div>
        )}
      </div>

      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="family_phone">
            Teléfono
          </label>

          <input
            id="family_phone"
            name="phone"
            type="tel"
            maxLength="30"
            value={formData.phone}
            onChange={handleChange}
            autoComplete="tel"
            disabled={isSubmitting}
          />
        </div>

        <div className="form-field">
          <label htmlFor="family_email">
            Correo electrónico
          </label>

          <input
            id="family_email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="family_address">
          Dirección
        </label>

        <input
          id="family_address"
          name="address"
          type="text"
          maxLength="255"
          value={formData.address}
          onChange={handleChange}
          autoComplete="street-address"
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label>
          <input
            name="is_primary_contact"
            type="checkbox"
            checked={
              formData.is_primary_contact
            }
            onChange={handleChange}
            disabled={isSubmitting}
          />

          {' '}Contacto principal
        </label>
      </div>

      {validationError && (
        <div
          className="form-message form-message--error"
          role="alert"
        >
          {validationError}
        </div>
      )}

      {error && (
        <div
          className="form-message form-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      {success && (
        <div
          className="form-message form-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      <div className="form-actions">
        <button
            className="button button--primary"
            type="submit"
            disabled={isSubmitting}
        >
            {isSubmitting
            ? (
              isEditing
                ? 'Guardando...'
                : 'Registrando...'
            )
            : (
              isEditing
                ? 'Guardar cambios'
                : 'Registrar familiar'
            )}
        </button>

        <button
            className="button button--secondary"
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
        >
            Cancelar
        </button>
      </div>
    </form>
  )
}

export default StudentFamilyMemberForm
