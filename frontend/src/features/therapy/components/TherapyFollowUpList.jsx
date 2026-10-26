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


function TherapyFollowUpList({
  followups,
  onEdit,
}) {
  if (followups.length === 0) {
    return (
      <div className="students-empty">
        No hay seguimientos terapéuticos registrados.
      </div>
    )
  }

  return (
    <div className="therapy-followup-list">
      {followups.map((followUp) => (
        <article
          className="therapy-followup-item"
          key={followUp.id}
        >
          <div className="therapy-followup-item__header">
            <div>
              <h3>{followUp.therapy_area}</h3>

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

          <dl className="therapy-followup-details">
            <div>
              <dt>Objetivos</dt>
              <dd>{followUp.objectives}</dd>
            </div>

            <div>
              <dt>Actividades realizadas</dt>
              <dd>{followUp.activities || '—'}</dd>
            </div>

            <div>
              <dt>Notas de progreso</dt>
              <dd>{followUp.progress_notes}</dd>
            </div>

            <div>
              <dt>Recomendaciones</dt>
              <dd>
                {followUp.recommendations || '—'}
              </dd>
            </div>
          </dl>

          <p className="therapy-followup-item__meta">
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


export default TherapyFollowUpList
