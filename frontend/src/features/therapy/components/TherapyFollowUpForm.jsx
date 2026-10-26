import { useState } from 'react'
import './TherapyFollowUp.css'


function getTodayDate() {
  const now = new Date()
  const timezoneOffset =
    now.getTimezoneOffset() * 60 * 1000

  return new Date(
    now.getTime() - timezoneOffset
  ).toISOString().slice(0, 10)
}


function TherapyFollowUpForm({
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
    therapy_area:
      initialFollowUp?.therapy_area ?? '',
    objectives:
      initialFollowUp?.objectives ?? '',
    activities:
      initialFollowUp?.activities ?? '',
    progress_notes:
      initialFollowUp?.progress_notes ?? '',
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
      therapy_area:
        formData.therapy_area.trim(),
      objectives:
        formData.objectives.trim(),
      activities:
        formData.activities.trim(),
      progress_notes:
        formData.progress_notes.trim(),
      recommendations:
        formData.recommendations.trim(),
    }

    if (
      !followUpData.followup_date
      || !followUpData.therapy_area
      || !followUpData.objectives
      || !followUpData.progress_notes
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
      className="student-form therapy-followup-form"
      onSubmit={handleSubmit}
    >
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="therapy-followup-date">
            Fecha del seguimiento
          </label>

          <input
            id="therapy-followup-date"
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
          <label htmlFor="therapy-area">
            Área terapéutica
          </label>

          <input
            id="therapy-area"
            name="therapy_area"
            type="text"
            maxLength="120"
            value={formData.therapy_area}
            onChange={handleChange}
            placeholder="Ej. Terapia ocupacional"
            required
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="therapy-objectives">
          Objetivos
        </label>

        <textarea
          id="therapy-objectives"
          name="objectives"
          rows="3"
          value={formData.objectives}
          onChange={handleChange}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="therapy-activities">
          Actividades realizadas
        </label>

        <textarea
          id="therapy-activities"
          name="activities"
          rows="3"
          value={formData.activities}
          onChange={handleChange}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="therapy-progress-notes">
          Notas de progreso
        </label>

        <textarea
          id="therapy-progress-notes"
          name="progress_notes"
          rows="4"
          value={formData.progress_notes}
          onChange={handleChange}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="therapy-recommendations">
          Recomendaciones
        </label>

        <textarea
          id="therapy-recommendations"
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


export default TherapyFollowUpForm
