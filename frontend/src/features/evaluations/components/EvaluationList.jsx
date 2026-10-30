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


function EvaluationList({
  evaluations,
  onEdit,
}) {
  if (!evaluations.length) {
    return (
      <div className="student-record-empty">
        No hay evaluaciones registradas.
      </div>
    )
  }

  return (
    <div className="evaluation-list">
      {evaluations.map((evaluation) => (
        <article
          className="evaluation-item"
          key={evaluation.id}
        >
          <div className="evaluation-item__header">
            <div>
              <h3>{evaluation.evaluation_type}</h3>
              <p>
                {formatDate(
                  evaluation.evaluation_date
                )}
              </p>
            </div>

            {onEdit && (
              <button
                className="button button--secondary"
                type="button"
                onClick={() => onEdit(evaluation)}
              >
                Editar
              </button>
            )}
          </div>

          <dl className="evaluation-details">
            <div>
              <dt>Resultados</dt>
              <dd>{evaluation.results}</dd>
            </div>

            <div>
              <dt>Observaciones</dt>
              <dd>
                {evaluation.observations || '—'}
              </dd>
            </div>
          </dl>

          <p className="evaluation-item__meta">
            Registrado por{' '}
            {evaluation.created_by?.first_name
              || evaluation.created_by?.username
              || 'usuario institucional'}
          </p>
        </article>
      ))}
    </div>
  )
}


export default EvaluationList
