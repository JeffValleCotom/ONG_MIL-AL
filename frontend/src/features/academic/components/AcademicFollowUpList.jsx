import { useState } from 'react'

import AppModal
  from '../../../components/ui/AppModal'

import './AcademicFollowUp.css'


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


function AcademicFollowUpList({
  followups,
  onEdit,
}) {
  const [
    selectedFollowUp,
    setSelectedFollowUp,
  ] = useState(null)

  if (followups.length === 0) {
    return (
      <div className="academic-followup-empty">
        <span aria-hidden="true">
          ○
        </span>

        <strong>
          Sin seguimientos académicos
        </strong>

        <p>
          Todavía no se han registrado seguimientos
          académicos para este estudiante.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="academic-followup-list">
        {followups.map((followUp) => (
          <article
            className="academic-followup-item"
            key={followUp.id}
          >
            <div className="academic-followup-item__main">
              <div className="academic-followup-item__topline">
                <span className="academic-followup-item__subject">
                  {followUp.subject}
                </span>

                <span className="academic-followup-item__date">
                  {formatDate(
                    followUp.followup_date,
                  )}
                </span>
              </div>

              <strong>
                {followUp.academic_period}
              </strong>

              <p>
                {followUp.observations}
              </p>
            </div>

            <div className="academic-followup-item__actions">
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
        title="Detalle académico"
        subtitle={
          'Consulta la información registrada '
          + 'para este seguimiento.'
        }
        onClose={() => {
          setSelectedFollowUp(null)
        }}
        size="lg"
      >
        {selectedFollowUp && (
          <div className="academic-followup-detail">
            <div className="academic-followup-detail__context">
              <div>
                <span>
                  Materia o área
                </span>

                <strong>
                  {selectedFollowUp.subject}
                </strong>
              </div>

              <div>
                <span>
                  Período
                </span>

                <strong>
                  {selectedFollowUp.academic_period}
                </strong>
              </div>

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
            </div>

            <dl className="academic-followup-details">
              <div>
                <dt>Observaciones</dt>
                <dd>
                  {selectedFollowUp.observations}
                </dd>
              </div>

              <div>
                <dt>Fortalezas</dt>
                <dd>
                  {selectedFollowUp.strengths || '—'}
                </dd>
              </div>

              <div>
                <dt>Áreas de mejora</dt>
                <dd>
                  {
                    selectedFollowUp
                      .areas_for_improvement
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

            <p className="academic-followup-item__meta">
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


export default AcademicFollowUpList
