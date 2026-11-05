import { useState } from 'react'

import './Evaluation.css'


function formatDate(value) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}/${month}/${year}`
}


function getUserDisplayName(user) {
  if (!user) {
    return 'Usuario institucional'
  }

  const fullName = [
    user.first_name,
    user.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return (
    fullName
    || user.username
    || 'Usuario institucional'
  )
}


function EvaluationList({
  evaluations,
  onEdit,
}) {
  const [
    expandedEvaluationId,
    setExpandedEvaluationId,
  ] = useState(null)

  if (!evaluations.length) {
    return (
      <div className="evaluation-empty">
        <span
          className="evaluation-empty__icon"
          aria-hidden="true"
        >
          ✓
        </span>

        <strong>
          Sin evaluaciones registradas
        </strong>

        <p>
          Las evaluaciones aparecerán aquí cuando
          sean registradas por un profesional
          autorizado.
        </p>
      </div>
    )
  }

  return (
    <div className="evaluation-list">
      {evaluations.map((evaluation) => {
        const isExpanded =
          expandedEvaluationId === evaluation.id

        return (
          <article
            className={
              isExpanded
                ? (
                    'evaluation-item '
                    + 'evaluation-item--expanded'
                  )
                : 'evaluation-item'
            }
            key={evaluation.id}
          >
            <div className="evaluation-item__summary">
              <span
                className="evaluation-item__icon"
                aria-hidden="true"
              >
                ✓
              </span>

              <div className="evaluation-item__main">
                <strong>
                  {evaluation.evaluation_type}
                </strong>

                <span>
                  {formatDate(
                    evaluation.evaluation_date,
                  )}
                </span>
              </div>

              <span className="evaluation-item__status">
                Registrada
              </span>

              <button
                className={
                  'evaluation-item__view '
                  + 'button button--secondary'
                }
                type="button"
                onClick={() => {
                  setExpandedEvaluationId(
                    isExpanded
                      ? null
                      : evaluation.id,
                  )
                }}
              >
                {isExpanded
                  ? 'Ocultar resultados'
                  : 'Ver resultados'}
              </button>
            </div>

            {isExpanded && (
              <div className="evaluation-item__details">
                <dl className="evaluation-details">
                  <div>
                    <dt>Resultados</dt>

                    <dd>
                      {evaluation.results}
                    </dd>
                  </div>

                  <div>
                    <dt>Observaciones</dt>

                    <dd>
                      {evaluation.observations || '—'}
                    </dd>
                  </div>
                </dl>

                <div className="evaluation-item__footer">
                  <p className="evaluation-item__meta">
                    Registrado por{' '}
                    {getUserDisplayName(
                      evaluation.created_by,
                    )}
                  </p>

                  {onEdit && (
                    <button
                      className="button button--secondary"
                      type="button"
                      onClick={() => {
                        onEdit(evaluation)
                      }}
                    >
                      Editar evaluación
                    </button>
                  )}
                </div>
              </div>
            )}
          </article>
        )
      })}
    </div>
  )
}


export default EvaluationList
