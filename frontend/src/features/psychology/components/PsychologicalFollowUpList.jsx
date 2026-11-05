import { useState } from 'react'

import AppModal
  from '../../../components/ui/AppModal'

import './PsychologicalFollowUp.css'


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
  const [
    selectedFollowUp,
    setSelectedFollowUp,
  ] = useState(null)

  if (followups.length === 0) {
    return (
      <div className="psychological-followup-empty">
        <span aria-hidden="true">
          ○
        </span>

        <strong>
          Sin seguimientos psicológicos
        </strong>

        <p>
          Todavía no se han registrado seguimientos
          psicológicos para este estudiante.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="psychological-followup-list">
        {followups.map((followUp) => (
          <article
            className="psychological-followup-item"
            key={followUp.id}
          >
            <div className="psychological-followup-item__main">
              <div className="psychological-followup-item__topline">
                <span className="psychological-followup-item__badge">
                  Seguimiento
                </span>

                <span className="psychological-followup-item__date">
                  {formatDate(
                    followUp.followup_date,
                  )}
                </span>
              </div>

              <strong>
                {followUp.reason}
              </strong>

              <p>
                {followUp.observations}
              </p>
            </div>

            <div className="psychological-followup-item__actions">
              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  setSelectedFollowUp(followUp)
                }}
              >
                Ver detalle
              </button>

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
          </article>
        ))}
      </div>

      <AppModal
        isOpen={Boolean(selectedFollowUp)}
        title="Detalle psicológico"
        subtitle={
          'Consulta la información registrada '
          + 'durante este seguimiento.'
        }
        onClose={() => {
          setSelectedFollowUp(null)
        }}
        size="lg"
      >
        {selectedFollowUp && (
          <div className="psychological-followup-detail">
            <div className="psychological-followup-detail__context">
              <div>
                <span>
                  Fecha
                </span>

                <strong>
                  {formatDate(
                    selectedFollowUp.followup_date,
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Motivo
                </span>

                <strong>
                  {selectedFollowUp.reason}
                </strong>
              </div>
            </div>

            <dl className="psychological-followup-details">
              <div>
                <dt>Observaciones</dt>
                <dd>
                  {selectedFollowUp.observations}
                </dd>
              </div>

              <div>
                <dt>
                  Notas emocionales y conductuales
                </dt>
                <dd>
                  {
                    selectedFollowUp
                      .emotional_behavioral_notes
                    || '—'
                  }
                </dd>
              </div>

              <div>
                <dt>Recomendaciones</dt>
                <dd>
                  {
                    selectedFollowUp
                      .recommendations
                    || '—'
                  }
                </dd>
              </div>
            </dl>

            <p className="psychological-followup-item__meta">
              Registrado por{' '}
              {getUserDisplayName(
                selectedFollowUp.created_by,
              )}
            </p>
          </div>
        )}
      </AppModal>
    </>
  )
}


export default PsychologicalFollowUpList
