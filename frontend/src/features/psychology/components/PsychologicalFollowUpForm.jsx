import { useState } from 'react'
import './PsychologicalFollowUp.css'


function getTodayDate() {
  const now = new Date()
  const timezoneOffset =
    now.getTimezoneOffset() * 60 * 1000

  return new Date(
    now.getTime() - timezoneOffset
  ).toISOString().slice(0, 10)
}


function PsychologicalFollowUpForm({
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
    reason:
      initialFollowUp?.reason ?? '',
    observations:
      initialFollowUp?.observations ?? '',
    emotional_behavioral_notes:
      initialFollowUp?.emotional_behavioral_notes ?? '',
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
      reason: formData.reason.trim(),
      observations: formData.observations.trim(),
      emotional_behavioral_notes:
        formData.emotional_behavioral_notes.trim(),
      recommendations:
        formData.recommendations.trim(),
    }

    if (
      !followUpData.followup_date
      || !followUpData.reason
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
      className="student-form psychological-followup-form"
      onSubmit={handleSubmit}
    >
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="psychological-followup-date">
            Fecha del seguimiento
          </label>

          <input
            id="psychological-followup-date"
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
          <label htmlFor="psychological-reason">
            Motivo del seguimiento
          </label>

          <input
            id="psychological-reason"
            name="reason"
            type="text"
            maxLength="200"
            value={formData.reason}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="psychological-observations">
          Observaciones
        </label>

        <textarea
          id="psychological-observations"
          name="observations"
          rows="4"
          value={formData.observations}
          onChange={handleChange}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="psychological-emotional-notes">
          Notas emocionales y conductuales
        </label>

        <textarea
          id="psychological-emotional-notes"
          name="emotional_behavioral_notes"
          rows="3"
          value={formData.emotional_behavioral_notes}
          onChange={handleChange}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="psychological-recommendations">
          Recomendaciones
        </label>

        <textarea
          id="psychological-recommendations"
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


export default PsychologicalFollowUpForm
