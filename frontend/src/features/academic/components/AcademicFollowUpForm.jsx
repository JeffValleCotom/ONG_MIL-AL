import { useState } from 'react'
import './AcademicFollowUp.css'

function getTodayDate() {
  const now = new Date()
  const timezoneOffset =
    now.getTimezoneOffset() * 60 * 1000

  return new Date(
    now.getTime() - timezoneOffset
  ).toISOString().slice(0, 10)
}


function AcademicFollowUpForm({
  initialFollowUp = null,
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = '',
}) {
  const isEditing = Boolean(initialFollowUp)

  const [formData, setFormData] = useState({
    followup_date:
      initialFollowUp?.followup_date ?? '',
    academic_period:
      initialFollowUp?.academic_period ?? '',
    subject:
      initialFollowUp?.subject ?? '',
    observations:
      initialFollowUp?.observations ?? '',
    strengths:
      initialFollowUp?.strengths ?? '',
    areas_for_improvement:
      initialFollowUp?.areas_for_improvement ?? '',
    recommendations:
      initialFollowUp?.recommendations ?? '',
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

    const followUpData = {
      followup_date: formData.followup_date,
      academic_period:
        formData.academic_period.trim(),
      subject:
        formData.subject.trim(),
      observations:
        formData.observations.trim(),
      strengths:
        formData.strengths.trim(),
      areas_for_improvement:
        formData.areas_for_improvement.trim(),
      recommendations:
        formData.recommendations.trim(),
    }

    if (
      !followUpData.followup_date
      || !followUpData.academic_period
      || !followUpData.subject
      || !followUpData.observations
    ) {
      setValidationError(
        'Completa todos los campos obligatorios.'
      )
      return
    }

    if (followUpData.followup_date > today) {
      setValidationError(
        'La fecha del seguimiento no puede ser futura.'
      )
      return
    }

    onSubmit?.(followUpData)
  }

  return (
    <form
      className="student-form academic-followup-form"
      onSubmit={handleSubmit}
    >
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="academic-followup-date">
            Fecha del seguimiento
          </label>

          <input
            id="academic-followup-date"
            name="followup_date"
            type="date"
            max={today}
            value={formData.followup_date}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>

        <div className="form-field">
          <label htmlFor="academic-period">
            Período académico
          </label>

          <input
            id="academic-period"
            name="academic_period"
            type="text"
            maxLength="50"
            value={formData.academic_period}
            onChange={handleChange}
            placeholder="Ej. 2026 - Ciclo 2"
            required
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="academic-subject">
          Materia o área
        </label>

        <input
          id="academic-subject"
          name="subject"
          type="text"
          maxLength="120"
          value={formData.subject}
          onChange={handleChange}
          placeholder="Ej. Matemática"
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="academic-observations">
          Observaciones
        </label>

        <textarea
          id="academic-observations"
          name="observations"
          rows="4"
          value={formData.observations}
          onChange={handleChange}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="academic-strengths">
          Fortalezas
        </label>

        <textarea
          id="academic-strengths"
          name="strengths"
          rows="3"
          value={formData.strengths}
          onChange={handleChange}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="academic-improvement">
          Áreas de mejora
        </label>

        <textarea
          id="academic-improvement"
          name="areas_for_improvement"
          rows="3"
          value={formData.areas_for_improvement}
          onChange={handleChange}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="academic-recommendations">
          Recomendaciones
        </label>

        <textarea
          id="academic-recommendations"
          name="recommendations"
          rows="3"
          value={formData.recommendations}
          onChange={handleChange}
          disabled={isSubmitting}
        />
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

      <div className="form-actions">
        {onCancel && (
          <button
            className="button button--secondary"
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </button>
        )}

        <button
          className="button button--primary"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? 'Guardando...'
            : (
              isEditing
                ? 'Guardar cambios'
                : 'Registrar seguimiento'
            )}
        </button>
      </div>
    </form>
  )
}


export default AcademicFollowUpForm
