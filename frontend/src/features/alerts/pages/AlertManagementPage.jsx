import {
  useEffect,
  useState,
} from 'react'

import {
  getAlerts,
  getAlertSummary,
  reviewAlert,
} from '../services/alertService'

import './AlertManagementPage.css'


const STATUS_LABELS = {
  OPEN: 'Pendiente',
  REVIEWED: 'Revisada',
  RESOLVED: 'Resuelta',
}


function formatDateTime(value) {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    }
  ).format(date)
}


function getUserName(user) {
  if (!user) {
    return 'Sistema'
  }

  const fullName = [
    user.first_name,
    user.last_name,
  ]
    .filter(Boolean)
    .join(' ')

  return fullName || user.username
}


function getErrorMessage(error) {
  const data = error?.data

  if (typeof data?.detail === 'string') {
    return data.detail
  }

  if (
    Array.isArray(data?.detail)
    && data.detail.length
  ) {
    return data.detail[0]
  }

  return (
    error?.message
    || 'No fue posible consultar las alertas.'
  )
}


async function fetchAlertData({
  studentContext,
  statusFilter,
}) {
  const [
    alertItems,
    alertSummary,
  ] = await Promise.all([
    getAlerts({
      context: studentContext,
      status: statusFilter,
    }),
    getAlertSummary(studentContext),
  ])

  return {
    alerts: Array.isArray(alertItems)
      ? alertItems
      : [],
    summary: alertSummary,
  }
}


export default function AlertManagementPage({
  studentContext,
  onOpenStudent,
  onSummaryChange,
}) {
  const [alerts, setAlerts] = useState([])
  const [summary, setSummary] = useState({
    open: 0,
    reviewed: 0,
    resolved: 0,
    total: 0,
  })

  const [statusFilter, setStatusFilter] =
    useState('')

  const [isLoading, setIsLoading] =
    useState(true)

  const [reviewingId, setReviewingId] =
    useState(null)

  const [error, setError] =
    useState('')


  useEffect(() => {
    let isMounted = true

    fetchAlertData({
        studentContext,
        statusFilter,
    })
        .then((data) => {
        if (!isMounted) {
            return
        }

        setAlerts(data.alerts)
        setSummary(data.summary)

        onSummaryChange?.(
            data.summary?.open ?? 0
        )

        setError('')
        })
        .catch((loadError) => {
        if (!isMounted) {
            return
        }

        setError(
            getErrorMessage(loadError)
        )
        })
        .finally(() => {
        if (isMounted) {
            setIsLoading(false)
        }
        })

    return () => {
        isMounted = false
    }
    }, [
    onSummaryChange,
    statusFilter,
    studentContext,
    ])

async function handleReview(alert) {
  setReviewingId(alert.id)
  setError('')

  try {
    await reviewAlert(
      alert.id,
      studentContext
    )

    const data = await fetchAlertData({
      studentContext,
      statusFilter,
    })

    setAlerts(data.alerts)
    setSummary(data.summary)

    onSummaryChange?.(
      data.summary?.open ?? 0
    )
  } catch (reviewError) {
    setError(
      getErrorMessage(reviewError)
    )
  } finally {
    setReviewingId(null)
  }
}

  return (
    <main className="alerts-page">
      <section className="alerts-overview">
        <article>
          <strong>{summary.open}</strong>
          <span>Pendientes</span>
        </article>

        <article>
          <strong>{summary.reviewed}</strong>
          <span>Revisadas</span>
        </article>

        <article>
          <strong>{summary.resolved}</strong>
          <span>Resueltas</span>
        </article>

        <article>
          <strong>{summary.total}</strong>
          <span>Historial total</span>
        </article>
      </section>

      <section className="alerts-toolbar">
        <div>
          <p className="alerts-eyebrow">
            Seguimiento operativo
          </p>

          <h2>
            Alertas
          </h2>

          <p>
            Condiciones objetivas detectadas en
            planes de intervención autorizados.
          </p>
        </div>

        <label>
          Estado

          <select
            value={statusFilter}
            onChange={(event) => {
                setIsLoading(true)
                setError('')
                setStatusFilter(
                    event.target.value
                )
                }}
          >
            <option value="">
              Todos
            </option>

            <option value="OPEN">
              Pendientes
            </option>

            <option value="REVIEWED">
              Revisadas
            </option>

            <option value="RESOLVED">
              Resueltas
            </option>
          </select>
        </label>
      </section>

      {error && (
        <div
          className="alerts-message alerts-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="alerts-empty">
          Cargando alertas...
        </div>
      ) : alerts.length === 0 ? (
        <div className="alerts-empty">
          No hay alertas para el estado
          seleccionado.
        </div>
      ) : (
        <section className="alerts-list">
          {alerts.map((alert) => (
            <article
              className="alert-card"
              key={alert.id}
            >
              <div className="alert-card__header">
                <div>
                  <span
                    className={
                      'alert-status '
                      + `alert-status--${alert.status
                        .toLowerCase()}`
                    }
                  >
                    {
                      STATUS_LABELS[
                        alert.status
                      ] ?? alert.status
                    }
                  </span>

                  <h3>
                    {alert.condition_label}
                  </h3>

                  <p>
                    {alert.student.first_name}
                    {' '}
                    {alert.student.last_name}
                    {' · '}
                    {
                      alert.student
                        .institutional_code
                    }
                  </p>
                </div>

                <time>
                  {
                    formatDateTime(
                      alert.detected_at
                    )
                  }
                </time>
              </div>

              <p className="alert-card__reason">
                {alert.reason}
              </p>

              <div className="alert-card__meta">
                <span>
                  Responsable:{' '}
                  <strong>
                    {
                      getUserName(
                        alert.assigned_to
                      )
                    }
                  </strong>
                </span>

                <span>
                  Rol:{' '}
                  <strong>
                    {alert.assigned_role}
                  </strong>
                </span>

                <span>
                  Plan:{' '}
                  <strong>
                    #{alert.intervention_plan.id}
                  </strong>
                </span>
              </div>

              <div className="alert-card__actions">
                <button
                  className={
                    'milal-button '
                    + 'milal-button--secondary'
                  }
                  type="button"
                  onClick={() => {
                    onOpenStudent?.(
                      alert.student
                    )
                  }}
                >
                  Ver estudiante
                </button>

                {alert.status === 'OPEN' && (
                  <button
                    className={
                      'milal-button '
                      + 'milal-button--primary'
                    }
                    type="button"
                    disabled={
                      reviewingId
                      === alert.id
                    }
                    onClick={() => {
                      handleReview(alert)
                    }}
                  >
                    {
                      reviewingId === alert.id
                        ? 'Guardando...'
                        : 'Marcar revisada'
                    }
                  </button>
                )}
              </div>

              <details className="alert-history">
                <summary>
                  Historial (
                  {alert.history?.length ?? 0}
                  )
                </summary>

                <div className="alert-history__items">
                  {(alert.history ?? []).map(
                    (event) => (
                      <article key={event.id}>
                        <div>
                          <strong>
                            {
                              event
                                .event_type_label
                            }
                          </strong>

                          <time>
                            {
                              formatDateTime(
                                event.created_at
                              )
                            }
                          </time>
                        </div>

                        {event.note && (
                          <p>
                            {event.note}
                          </p>
                        )}

                        <small>
                          {
                            getUserName(
                              event.performed_by
                            )
                          }
                        </small>
                      </article>
                    )
                  )}
                </div>
              </details>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}
