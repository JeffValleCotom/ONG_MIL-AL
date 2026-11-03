import { useState } from 'react'

import './StudentEvolutionPanel.css'


const EVIDENCE_LABELS = {
  strengths: 'Fortalezas',
  areas_for_improvement: 'Áreas de mejora',
  observations: 'Observaciones',
  recommendations: 'Recomendaciones',
  emotional_behavioral_notes:
    'Notas emocionales y conductuales',
  progress_notes: 'Notas de progreso',
  objectives: 'Objetivos',
  activities: 'Actividades realizadas',
  results: 'Resultados',
}

const TYPE_LABELS = {
  ACADEMIC_FOLLOWUP: 'Seguimiento académico',
  PSYCHOLOGICAL_FOLLOWUP:
    'Seguimiento psicológico',
  THERAPY_FOLLOWUP: 'Seguimiento terapéutico',
  EVALUATION: 'Evaluación',
}

const EMPTY_PERIODS = []


function formatPeriod(value) {
  if (!value) {
    return '—'
  }

  const [year, month] = value.split('-')

  const date = new Date(
    Date.UTC(
      Number(year),
      Number(month) - 1,
      1
    )
  )

  const label = new Intl.DateTimeFormat(
    'es-GT',
    {
      month: 'long',
      year: 'numeric',
      timeZone: 'UTC',
    }
  ).format(date)

  return (
    label.charAt(0).toUpperCase()
    + label.slice(1)
  )
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


function formatDelta(value) {
  if (value > 0) {
    return `+${value}`
  }

  return String(value)
}


function PeriodEvidence({
  period,
}) {
  if (!period) {
    return null
  }

  return (
    <div className="student-evolution__comparison-period">
      <h4>{formatPeriod(period.period)}</h4>

      <div className="student-evolution__comparison-counts">
        <span>
          {period.total_records} registros
        </span>

        <span>
          {period.followup_count} seguimientos
        </span>

        <span>
          {period.evaluation_count} evaluaciones
        </span>
      </div>

      <div className="student-evolution__evidence-list">
        {period.records.map((record) => (
          <article
            className="student-evolution__evidence"
            key={
              `${record.record_type}-${record.record_id}`
            }
          >
            <div className="student-evolution__evidence-header">
              <strong>{record.title}</strong>

              <span>
                {formatDate(record.date)}
              </span>
            </div>

            <p className="student-evolution__evidence-type">
              {TYPE_LABELS[record.record_type]
                ?? record.record_type}
            </p>

            {record.evidence.length > 0 ? (
              <dl>
                {record.evidence.map((item) => (
                  <div key={item.field}>
                    <dt>
                      {EVIDENCE_LABELS[item.field]
                        ?? item.field}
                    </dt>
                    <dd>{item.value}</dd>
                  </div>
                ))}
              </dl>
            ) : (
              <p className="student-evolution__empty-evidence">
                El registro no contiene evidencia
                cualitativa adicional.
              </p>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}


function StudentEvolutionPanel({
  evolution,
}) {
  const summary = evolution?.summary
  const periods =
    evolution?.periods ?? EMPTY_PERIODS

  const [
    previousPeriodKey,
    setPreviousPeriodKey,
  ] = useState('')

  const [
    currentPeriodKey,
    setCurrentPeriodKey,
  ] = useState('')

  const resolvedCurrentPeriodKey = (
    periods.some(
      (period) => (
        period.period === currentPeriodKey
      )
    )
      ? currentPeriodKey
      : periods[0]?.period ?? ''
  )

  const resolvedPreviousPeriodKey = (
    periods.some(
      (period) => (
        period.period === previousPeriodKey
      )
    )
      ? previousPeriodKey
      : (
        periods[1]?.period
        ?? periods[0]?.period
        ?? ''
      )
  )

  const previousPeriod = periods.find(
    (period) => (
      period.period === resolvedPreviousPeriodKey
    )
  )

  const currentPeriod = periods.find(
    (period) => (
      period.period === resolvedCurrentPeriodKey
    )
  )

  const maxRecords = Math.max(
    1,
    ...periods.map(
      (period) => period.total_records
    )
  )

  if (!summary) {
    return null
  }

  return (
    <div className="student-evolution">
      <div className="student-evolution__summary">
        <div>
          <strong>{summary.total_records}</strong>
          <span>Registros</span>
        </div>

        <div>
          <strong>{summary.followup_count}</strong>
          <span>Seguimientos</span>
        </div>

        <div>
          <strong>{summary.evaluation_count}</strong>
          <span>Evaluaciones</span>
        </div>

        <div>
          <strong>{summary.period_count}</strong>
          <span>Períodos con actividad</span>
        </div>
      </div>

      {periods.length === 0 ? (
        <div className="student-record-empty">
          No hay información suficiente para
          visualizar evolución.
        </div>
      ) : (
        <>
          <section className="student-evolution__activity">
            <div className="student-evolution__subheader">
              <div>
                <h3>
                  Actividad registrada por período
                </h3>

                <p>
                  Representa cantidad de registros,
                  no una puntuación de progreso.
                </p>
              </div>
            </div>

            <div className="student-evolution__bars">
              {periods.map((period) => {
                const width = (
                  period.total_records
                  / maxRecords
                ) * 100

                return (
                  <div
                    className="student-evolution__bar-row"
                    key={period.period}
                  >
                    <span>
                      {formatPeriod(period.period)}
                    </span>

                    <div className="student-evolution__bar-track">
                      <div
                        className="student-evolution__bar"
                        style={{
                          width: `${width}%`,
                        }}
                      />
                    </div>

                    <strong>
                      {period.total_records}
                    </strong>
                  </div>
                )
              })}
            </div>
          </section>

          <section className="student-evolution__comparison">
            <div className="student-evolution__subheader">
              <div>
                <h3>Comparación por períodos</h3>

                <p>
                  Compara actividad y evidencia
                  cualitativa registrada.
                </p>
              </div>
            </div>

            <div className="student-evolution__selectors">
              <label>
                Período anterior

                <select
                  value={resolvedPreviousPeriodKey}
                  onChange={(event) => {
                    setPreviousPeriodKey(
                      event.target.value
                    )
                  }}
                >
                  {periods.map((period) => (
                    <option
                      key={period.period}
                      value={period.period}
                    >
                      {formatPeriod(period.period)}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Período de comparación

                <select
                  value={resolvedCurrentPeriodKey}
                  onChange={(event) => {
                    setCurrentPeriodKey(
                      event.target.value
                    )
                  }}
                >
                  {periods.map((period) => (
                    <option
                      key={period.period}
                      value={period.period}
                    >
                      {formatPeriod(period.period)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {previousPeriod && currentPeriod && (
              <>
                <div className="student-evolution__deltas">
                  <div>
                    <span>
                      Variación de registros
                    </span>
                    <strong>
                      {formatDelta(
                        currentPeriod.total_records
                        - previousPeriod.total_records
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Variación de seguimientos
                    </span>
                    <strong>
                      {formatDelta(
                        currentPeriod.followup_count
                        - previousPeriod.followup_count
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Variación de evaluaciones
                    </span>
                    <strong>
                      {formatDelta(
                        currentPeriod.evaluation_count
                        - previousPeriod.evaluation_count
                      )}
                    </strong>
                  </div>
                </div>

                <div className="student-evolution__period-grid">
                  <PeriodEvidence
                    period={previousPeriod}
                  />

                  <PeriodEvidence
                    period={currentPeriod}
                  />
                </div>
              </>
            )}
          </section>
        </>
      )}
    </div>
  )
}


export default StudentEvolutionPanel
