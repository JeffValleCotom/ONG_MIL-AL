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
  if (!items.length) {
    return (
      <div className="student-record-empty">
        No hay registros disponibles en el historial.
      </div>
    )
  }

  return (
    <div className="student-history">
      {items.map((item) => {
        const detailEntries = Object.entries(
          item.details ?? {}
        ).filter(([, value]) => (
          value !== null
          && value !== undefined
          && String(value).trim() !== ''
        ))

        return (
          <article
            className="student-history__item"
            key={
              `${item.record_type}-${item.record_id}`
            }
          >
            <div className="student-history__marker" />

            <div className="student-history__content">
              <div className="student-history__header">
                <div>
                  <div className="student-history__tags">
                    <span className="student-history__tag">
                      {AREA_LABELS[item.area]
                        ?? item.area}
                    </span>

                    <span className="student-history__type">
                      {TYPE_LABELS[item.record_type]
                        ?? item.record_type}
                    </span>
                  </div>

                  <h3>{item.title}</h3>
                </div>

                <time dateTime={item.date}>
                  {formatDate(item.date)}
                </time>
              </div>

              {detailEntries.length > 0 && (
                <dl className="student-history__details">
                  {detailEntries.map(
                    ([key, value]) => (
                      <div key={key}>
                        <dt>
                          {DETAIL_LABELS[key] ?? key}
                        </dt>
                        <dd>{value}</dd>
                      </div>
                    )
                  )}
                </dl>
              )}

              <p className="student-history__meta">
                Registrado por{' '}
                {getUserName(item.created_by)}
              </p>
            </div>
          </article>
        )
      })}
    </div>
  )
}


export default StudentHistoryTimeline
