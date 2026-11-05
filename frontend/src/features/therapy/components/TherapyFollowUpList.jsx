import { useState } from 'react'


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
  const [
    expandedFollowUpId,
    setExpandedFollowUpId,
  ] = useState(null)

  if (followups.length === 0) {
    return (
      <div className="therapy-followup-empty">
        <span
          className="therapy-followup-empty__icon"
          aria-hidden="true"
        >
          ○
        </span>

        <strong>
          Sin sesiones registradas
        </strong>

        <p>
          Los seguimientos terapéuticos aparecerán
          aquí cuando sean registrados.
        </p>
      </div>
    )
  }

  return (
    <div className="therapy-followup-list">
      {followups.map((followUp) => {
        const isExpanded =
          expandedFollowUpId === followUp.id

        return (
          <article
            className={
              isExpanded
                ? (
                    'therapy-followup-item '
                    + 'therapy-followup-item--expanded'
                  )
                : 'therapy-followup-item'
            }
            key={followUp.id}
          >
            <div className="therapy-followup-item__summary">
              <span
                className="therapy-followup-item__marker"
                aria-hidden="true"
              >
                ✓
              </span>

              <div className="therapy-followup-item__date">
                <strong>
                  {formatDate(
                    followUp.followup_date,
                  )}
                </strong>

                <span>
                  Sesión terapéutica
                </span>
              </div>

              <div className="therapy-followup-item__main">
                <strong>
                  {followUp.therapy_area}
                </strong>

                <span>
                  {followUp.objectives}
                </span>
              </div>

              <button
                className={
                  'therapy-followup-item__view '
                  + 'button button--secondary'
                }
                type="button"
                onClick={() => {
                  setExpandedFollowUpId(
                    isExpanded
                      ? null
                      : followUp.id,
                  )
                }}
              >
                {isExpanded
                  ? 'Ocultar'
                  : 'Ver'}
              </button>
            </div>

            {isExpanded && (
              <div className="therapy-followup-item__details">
                <dl className="therapy-followup-details">
                  <div>
                    <dt>Objetivos</dt>
                    <dd>
                      {followUp.objectives}
                    </dd>
                  </div>

                  <div>
                    <dt>Actividades realizadas</dt>
                    <dd>
                      {followUp.activities || '—'}
                    </dd>
                  </div>

                  <div>
                    <dt>Notas de progreso</dt>
                    <dd>
                      {followUp.progress_notes}
                    </dd>
                  </div>

                  <div>
                    <dt>Recomendaciones</dt>
                    <dd>
                      {followUp.recommendations || '—'}
                    </dd>
                  </div>
                </dl>

                <div className="therapy-followup-item__footer">
                  <p className="therapy-followup-item__meta">
                    Registrado por{' '}
                    {getUserDisplayName(
                      followUp.created_by,
                    )}
                  </p>

                  {onEdit && (
                    <button
                      className="button button--secondary"
                      type="button"
                      onClick={() => {
                        onEdit(followUp)
                      }}
                    >
                      Editar seguimiento
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


export default TherapyFollowUpList
