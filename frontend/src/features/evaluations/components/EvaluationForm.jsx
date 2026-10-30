import { useState } from 'react'
import './Evaluation.css'


function getTodayDate() {
  const now = new Date()
  const timezoneOffset =
    now.getTimezoneOffset() * 60 * 1000

  return new Date(
    now.getTime() - timezoneOffset
  ).toISOString().slice(0, 10)
}


function EvaluationForm({
  initialEvaluation = null,
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = '',
}) {
  const isEditing = Boolean(initialEvaluation)

  const [formData, setFormData] = useState({
    evaluation_date:
      initialEvaluation?.evaluation_date ?? '',
    evaluation_type:
      initialEvaluation?.evaluation_type ?? '',
    results:
      initialEvaluation?.results ?? '',
    observations:
      initialEvaluation?.observations ?? '',
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

    const evaluationData = {
      evaluation_date:
        formData.evaluation_date,
      evaluation_type:
        formData.evaluation_type.trim(),
      results:
        formData.results.trim(),
      observations:
        formData.observations.trim(),
    }

    if (
      !evaluationData.evaluation_date
      || !evaluationData.evaluation_type
      || !evaluationData.results
    ) {
      setValidationError(
        'Completa todos los campos obligatorios.'
      )
      return
    }

    if (evaluationData.evaluation_date > today) {
      setValidationError(
        'La fecha de la evaluación no puede ser futura.'
      )
      return
    }

    onSubmit?.(evaluationData)
  }

  return (
    <form
      className="student-form evaluation-form"
      onSubmit={handleSubmit}
    >
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="evaluation-date">
            Fecha de evaluación
          </label>

          <input
            id="evaluation-date"
            name="evaluation_date"
            type="date"
            max={today}
            value={formData.evaluation_date}
            onChange={handleChange}
            required
            disabled={isSubmitting}
          />
        </div>

        <div className="form-field">
          <label htmlFor="evaluation-type">
            Tipo de evaluación
          </label>

          <input
            id="evaluation-type"
            name="evaluation_type"
            type="text"
            maxLength="120"
            value={formData.evaluation_type}
            onChange={handleChange}
            placeholder="Ej. Evaluación de motricidad fina"
            required
            disabled={isSubmitting}
          />
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="evaluation-results">
          Resultados
        </label>

        <textarea
          id="evaluation-results"
          name="results"
          rows="4"
          value={formData.results}
          onChange={handleChange}
          required
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="evaluation-observations">
          Observaciones
        </label>

        <textarea
          id="evaluation-observations"
          name="observations"
          rows="3"
          value={formData.observations}
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
                : 'Registrar evaluación'
            )}
        </button>
      </div>
    </form>
  )
}


export default EvaluationForm
