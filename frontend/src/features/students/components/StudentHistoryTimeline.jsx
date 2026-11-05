import { useState } from 'react'

import AppModal
  from '../../../components/ui/AppModal'

import './StudentHistoryTimeline.css'


const AREA_LABELS = {
  ACADEMICA: 'Académica',
  PSICOLOGICA: 'Psicológica',
  TERAPEUTICA: 'Terapéutica',
}


const TYPE_LABELS = {
  ACADEMIC_FOLLOWUP: 'Seguimiento académico',
  PSYCHOLOGICAL_FOLLOWUP:
    'Seguimiento psicológico',
  THERAPY_FOLLOWUP: 'Seguimiento terapéutico',
  EVALUATION: 'Evaluación',
}


const DETAIL_LABELS = {
  academic_period: 'Período académico',
  subject: 'Asignatura',
  observations: 'Observaciones',
  strengths: 'Fortalezas',
  areas_for_improvement: 'Áreas de mejora',
  recommendations: 'Recomendaciones',
  reason: 'Motivo',
  emotional_behavioral_notes:
    'Notas emocionales y conductuales',
  therapy_area: 'Área terapéutica',
  objectives: 'Objetivos',
  activities: 'Actividades realizadas',
  progress_notes: 'Notas de progreso',
  evaluation_type: 'Tipo de evaluación',
  results: 'Resultados',
}


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


function getUserName(user) {
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


function StudentHistoryTimeline({
  items = [],
}) {
  const [
    selectedItem,
    setSelectedItem,
  ] = useState(null)

  if (!items.length) {
    return (
      <div className="student-history__empty">
        <span aria-hidden="true">
          ○
        </span>

        <strong>
          Sin registros en el historial
        </strong>

        <p>
          Todavía no hay información disponible
          para construir el historial integral.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="student-history">
        {items.map((item) => (
          <article
            className="student-history__item"
            key={
              `${item.record_type}-${item.record_id}`
            }
          >
            <div className="student-history__main">
              <div className="student-history__tags">
                <span className="student-history__tag">
                  {AREA_LABELS[item.area]
                    ?? item.area}
                </span>

                <span className="student-history__type">
                  {TYPE_LABELS[item.record_type]
                    ?? item.record_type}
                </span>

                <time dateTime={item.date}>
                  {formatDate(item.date)}
                </time>
              </div>

              <strong className="student-history__title">
                {item.title}
              </strong>

              <p className="student-history__meta">
                Registrado por{' '}
                {getUserName(item.created_by)}
              </p>
            </div>

            <button
              className="milal-button milal-button--secondary"
              type="button"
              onClick={() => {
                setSelectedItem(item)
              }}
            >
              Ver detalle
            </button>
          </article>
        ))}
      </div>

      <AppModal
        isOpen={Boolean(selectedItem)}
        title="Detalle del historial"
        subtitle={
          'Consulta la información registrada '
          + 'durante este seguimiento.'
        }
        onClose={() => {
          setSelectedItem(null)
        }}
        size="lg"
      >
        {selectedItem && (() => {
          const detailEntries = Object.entries(
            selectedItem.details ?? {},
          ).filter(([, value]) => (
            value !== null
            && value !== undefined
            && String(value).trim() !== ''
          ))

          return (
            <div className="student-history-detail">
              <div className="student-history-detail__context">
                <div>
                  <span>Área</span>

                  <strong>
                    {AREA_LABELS[selectedItem.area]
                      ?? selectedItem.area}
                  </strong>
                </div>

                <div>
                  <span>Tipo</span>

                  <strong>
                    {
                      TYPE_LABELS[
                        selectedItem.record_type
                      ]
                      ?? selectedItem.record_type
                    }
                  </strong>
                </div>

                <div>
                  <span>Fecha</span>

                  <strong>
                    {formatDate(selectedItem.date)}
                  </strong>
                </div>
              </div>

              <h3 className="student-history-detail__title">
                {selectedItem.title}
              </h3>

              {detailEntries.length > 0 ? (
                <dl className="student-history__details">
                  {detailEntries.map(
                    ([key, value]) => (
                      <div key={key}>
                        <dt>
                          {DETAIL_LABELS[key] ?? key}
                        </dt>

                        <dd>
                          {value}
                        </dd>
                      </div>
                    ),
                  )}
                </dl>
              ) : (
                <p className="student-history-detail__empty">
                  Este registro no contiene información
                  adicional.
                </p>
              )}

              <p className="student-history__meta">
                Registrado por{' '}
                {getUserName(
                  selectedItem.created_by,
                )}
              </p>
            </div>
          )
        })()}
      </AppModal>
    </>
  )
}


export default StudentHistoryTimeline
