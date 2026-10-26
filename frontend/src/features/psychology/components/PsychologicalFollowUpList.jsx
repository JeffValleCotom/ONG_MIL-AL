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
    return '—'
  }

  const fullName = [
    user.first_name,
    user.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return fullName || user.username || '—'
}


function PsychologicalFollowUpList({
  followups,
  onEdit,
}) {
  if (followups.length === 0) {
    return (
      <div className="students-empty">
        No hay seguimientos psicológicos registrados.
      </div>
    )
  }

  return (
    <div className="psychological-followup-list">
      {followups.map((followUp) => (
        <article
          className="psychological-followup-item"
          key={followUp.id}
        >
          <div className="psychological-followup-item__header">
            <div>
              <h3>{followUp.reason}</h3>

              <p>
                {formatDate(followUp.followup_date)}
              </p>
            </div>

            {onEdit && (
              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  onEdit(followUp)
                }}
              >
                Editar
              </button>
            )}
          </div>

          <dl className="psychological-followup-details">
            <div>
              <dt>Observaciones</dt>
              <dd>{followUp.observations}</dd>
            </div>

            <div>
              <dt>
                Notas emocionales y conductuales
              </dt>
              <dd>
                {
                  followUp.emotional_behavioral_notes
                  || '—'
                }
              </dd>
            </div>

            <div>
              <dt>Recomendaciones</dt>
              <dd>
                {followUp.recommendations || '—'}
              </dd>
            </div>
          </dl>

          <p className="psychological-followup-item__meta">
            Registrado por{' '}
            {getUserDisplayName(
              followUp.created_by
            )}
          </p>
        </article>
      ))}
    </div>
  )
}


export default PsychologicalFollowUpList
