import { useState } from 'react'

function getTodayDate() {
  const now = new Date()
  const timezoneOffset = now.getTimezoneOffset() * 60 * 1000

  return new Date(
    now.getTime() - timezoneOffset
  ).toISOString().slice(0, 10)
}

function StudentRegistrationForm({
  onSubmit,
  isSubmitting = false,
  error = '',
  success = '',
}) {
  const [formData, setFormData] = useState({
    institutional_code: '',
    first_name: '',
    last_name: '',
    date_of_birth: '',
    admission_date: '',
  })

  const [validationError, setValidationError] =
    useState('')

  const today = getTodayDate()

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((current) => ({
      ...current,
      [name]: value,
    }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    setValidationError('')

    const studentData = {
      institutional_code:
        formData.institutional_code.trim().toUpperCase(),
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      date_of_birth: formData.date_of_birth,
      admission_date: formData.admission_date,
    }

    if (
      !studentData.institutional_code ||
      !studentData.first_name ||
      !studentData.last_name
    ) {
      setValidationError(
        'Completa todos los campos obligatorios.'
      )
      return
    }

    if (
      studentData.date_of_birth > today ||
      studentData.admission_date > today
    ) {
      setValidationError(
        'Las fechas no pueden ser futuras.'
      )
      return
    }

    if (
      studentData.admission_date <
      studentData.date_of_birth
    ) {
      setValidationError(
        'La fecha de ingreso no puede ser anterior '
        + 'a la fecha de nacimiento.'
      )
      return
    }

    onSubmit?.(studentData)
  }

  return (
    <form
      className="student-form"
      onSubmit={handleSubmit}
    >
      <div className="form-field">
        <label htmlFor="institutional_code">
          Código institucional
        </label>

        <input
          id="institutional_code"
          name="institutional_code"
          type="text"
          maxLength="30"
          value={formData.institutional_code}
          onChange={handleChange}
          required
          disabled={isSubmitting}
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
            maxLength="100"
            value={formData.first_name}
            onChange={handleChange}
            required
            autoComplete="given-name"
            disabled={isSubmitting}
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
          <label htmlFor="date_of_birth">
            Fecha de nacimiento
          </label>

          <input
            id="date_of_birth"
            name="date_of_birth"
            type="date"
            max={today}
            value={formData.date_of_birth}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>

        <div className="form-field">
          <label htmlFor="admission_date">
            Fecha de ingreso
          </label>

          <input
            id="admission_date"
            name="admission_date"
            type="date"
            max={today}
            value={formData.admission_date}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>
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
            ? 'Registrando...'
            : 'Registrar estudiante'}
        </button>
      </div>
    </form>
  )
}

export default StudentRegistrationForm
