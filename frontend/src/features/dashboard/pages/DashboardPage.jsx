import { useEffect, useMemo, useState } from 'react'

import { getDashboardOverview }
  from '../services/dashboardService'

import './DashboardPage.css'


const AREA_LABELS = {
  academic: 'Académico',
  psychological: 'Psicológico',
  therapy: 'Terapéutico',
  evaluations: 'Evaluaciones',
  interventions: 'Intervenciones',
}


function getDashboardErrorMessage(error) {
  const data = error?.data

  if (data) {
    const fields = [
      'context',
      'date_from',
      'date_to',
      'detail',
      'non_field_errors',
    ]

    for (const field of fields) {
      const value = data[field]

      if (Array.isArray(value) && value.length > 0) {
        return value[0]
      }

      if (typeof value === 'string' && value) {
        return value
      }
    }
  }

  return (
    error?.message
    || 'No fue posible cargar el dashboard.'
  )
}


function formatPeriod(period) {
  if (!period) {
    return ''
  }

  const [year, month] = period.split('-')

  if (!year || !month) {
    return period
  }

  const date = new Date(
    Number(year),
    Number(month) - 1,
    1
  )

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      month: 'short',
      year: 'numeric',
    }
  ).format(date)
}


function DashboardStat({
  value,
  label,
  detail,
  tone = 'default',
}) {
  return (
    <article
      className={
        `dashboard-stat dashboard-stat--${tone}`
      }
    >
      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>

      {detail && (
        <small>
          {detail}
        </small>
      )}
    </article>
  )
}


function DashboardPage({
  studentContext,
}) {
  const [dashboard, setDashboard] =
    useState(null)

  const [isLoading, setIsLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [filterForm, setFilterForm] =
    useState({
      dateFrom: '',
      dateTo: '',
    })

  const [filters, setFilters] =
    useState({
      dateFrom: '',
      dateTo: '',
    })

  useEffect(() => {
    let isMounted = true

    async function loadDashboard() {
      setIsLoading(true)
      setError('')

      try {
        const data = await getDashboardOverview({
          context: studentContext,
          dateFrom: filters.dateFrom,
          dateTo: filters.dateTo,
        })

        if (isMounted) {
          setDashboard(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            getDashboardErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      isMounted = false
    }
  }, [
    filters,
    studentContext,
  ])

  const timelineMax = useMemo(() => {
    if (!dashboard?.timeline?.length) {
      return 0
    }

    return Math.max(
      ...dashboard.timeline.flatMap(
        (period) => (
          dashboard.visible_areas.map(
            (area) => period[area] ?? 0
          )
        )
      ),
      0
    )
  }, [dashboard])

  function handleFilterSubmit(event) {
    event.preventDefault()

    setFilters({
      dateFrom: filterForm.dateFrom,
      dateTo: filterForm.dateTo,
    })
  }

  function handleClearFilters() {
    const emptyFilters = {
      dateFrom: '',
      dateTo: '',
    }

    setFilterForm(emptyFilters)
    setFilters(emptyFilters)
  }

  const indicators =
    dashboard?.activity?.indicators ?? {}

  const interventionIndicators =
    indicators.interventions ?? null

  const simpleAreas = (
    dashboard?.visible_areas ?? []
  ).filter(
    (area) => area !== 'interventions'
  )

  return (
    <main className="dashboard-page">
      <section className="dashboard-filter-card">
        <div className="dashboard-filter-card__heading">
          <div>
            <p className="dashboard-eyebrow">
              Periodo de análisis
            </p>

            <h2>
              Indicadores de seguimiento
            </h2>

            <p>
              Consulta los registros disponibles
              dentro de un periodo específico.
            </p>
          </div>
        </div>

        <form
          className="dashboard-filter"
          onSubmit={handleFilterSubmit}
        >
          <div className="dashboard-field">
            <label htmlFor="dashboard-date-from">
              Desde
            </label>

            <input
              id="dashboard-date-from"
              type="date"
              value={filterForm.dateFrom}
              onChange={(event) => {
                setFilterForm((current) => ({
                  ...current,
                  dateFrom: event.target.value,
                }))
              }}
            />
          </div>

          <div className="dashboard-field">
            <label htmlFor="dashboard-date-to">
              Hasta
            </label>

            <input
              id="dashboard-date-to"
              type="date"
              value={filterForm.dateTo}
              onChange={(event) => {
                setFilterForm((current) => ({
                  ...current,
                  dateTo: event.target.value,
                }))
              }}
            />
          </div>

          <div className="dashboard-filter__actions">
            <button
              className="milal-button milal-button--primary"
              type="submit"
            >
              Aplicar
            </button>

            <button
              className="milal-button milal-button--secondary"
              type="button"
              onClick={handleClearFilters}
            >
              Limpiar
            </button>
          </div>
        </form>
      </section>

      {error && (
        <div
          className="dashboard-message dashboard-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      {isLoading && (
        <section className="dashboard-loading">
          Cargando indicadores...
        </section>
      )}

      {!isLoading && !error && dashboard && (
        <>
          <section
            className="dashboard-summary"
            aria-label="Resumen general"
          >
            <DashboardStat
              value={dashboard.students.total}
              label="Estudiantes visibles"
              detail="Según tu contexto profesional"
              tone="primary"
            />

            <DashboardStat
              value={dashboard.students.active}
              label="Estudiantes activos"
              detail="Estado actual"
              tone="success"
            />

            <DashboardStat
              value={dashboard.students.inactive}
              label="Estudiantes inactivos"
              detail="Estado actual"
            />

            <DashboardStat
              value={
                dashboard.activity.total_records
              }
              label="Registros del periodo"
              detail={
                filters.dateFrom || filters.dateTo
                  ? 'Periodo seleccionado'
                  : 'Todo el historial disponible'
              }
              tone="primary"
            />
          </section>

          <section className="dashboard-section">
            <div className="dashboard-section__heading">
              <div>
                <p className="dashboard-eyebrow">
                  Seguimiento
                </p>

                <h2>
                  Actividad por área
                </h2>

                <p>
                  Registros reales disponibles
                  para tu contexto de acceso.
                </p>
              </div>
            </div>

            <div className="dashboard-indicators">
              {simpleAreas.map((area) => (
                <article
                  className="dashboard-indicator"
                  key={area}
                >
                  <span>
                    {AREA_LABELS[area] ?? area}
                  </span>

                  <strong>
                    {indicators[area] ?? 0}
                  </strong>

                  <small>
                    registros
                  </small>
                </article>
              ))}
            </div>
          </section>

          {interventionIndicators && (
            <section className="dashboard-section">
              <div className="dashboard-section__heading">
                <div>
                  <p className="dashboard-eyebrow">
                    Intervenciones
                  </p>

                  <h2>
                    Estado de intervenciones
                  </h2>

                  <p>
                    Seguimiento de las planificaciones
                    registradas en el periodo.
                  </p>
                </div>
              </div>

              <div className="dashboard-interventions">
                <DashboardStat
                  value={
                    interventionIndicators.plans
                  }
                  label="Planes"
                />

                <DashboardStat
                  value={
                    interventionIndicators.planned
                  }
                  label="Planificadas"
                />

                <DashboardStat
                  value={
                    interventionIndicators.in_progress
                  }
                  label="En progreso"
                  tone="primary"
                />

                <DashboardStat
                  value={
                    interventionIndicators.completed
                  }
                  label="Completadas"
                  tone="success"
                />

                <DashboardStat
                  value={
                    interventionIndicators.cancelled
                  }
                  label="Canceladas"
                />

                <DashboardStat
                  value={
                    interventionIndicators.followups
                  }
                  label="Avances registrados"
                />
              </div>

              {interventionIndicators.direct_records > 0 && (
                <p className="dashboard-legacy-note">
                  También existen{' '}
                  <strong>
                    {
                      interventionIndicators
                        .direct_records
                    }
                  </strong>{' '}
                  registros directos históricos de
                  intervenciones.
                </p>
              )}
            </section>
          )}

          <section className="dashboard-section">
            <div className="dashboard-section__heading">
              <div>
                <p className="dashboard-eyebrow">
                  Evolución temporal
                </p>

                <h2>
                  Actividad mensual
                </h2>

                <p>
                  Distribución de registros por mes
                  y área de seguimiento.
                </p>
              </div>
            </div>

            {dashboard.timeline.length === 0 ? (
              <div className="dashboard-empty">
                No hay actividad registrada para
                el periodo seleccionado.
              </div>
            ) : (
              <div className="dashboard-timeline">
                {dashboard.timeline.map((period) => (
                  <article
                    className="dashboard-period"
                    key={period.period}
                  >
                    <div className="dashboard-period__label">
                      {formatPeriod(period.period)}
                    </div>

                    <div className="dashboard-period__areas">
                      {dashboard.visible_areas.map(
                        (area) => {
                          const value =
                            period[area] ?? 0

                          const width = timelineMax > 0
                            ? (
                                value
                                / timelineMax
                                * 100
                              )
                            : 0

                          return (
                            <div
                              className="dashboard-period__area"
                              key={area}
                            >
                              <div
                                className={
                                  'dashboard-period__area-label'
                                }
                              >
                                <span>
                                  {
                                    AREA_LABELS[area]
                                    ?? area
                                  }
                                </span>

                                <strong>
                                  {value}
                                </strong>
                              </div>

                              <div
                                className="dashboard-bar"
                                aria-hidden="true"
                              >
                                <span
                                  style={{
                                    width:
                                      `${width}%`,
                                  }}
                                />
                              </div>
                            </div>
                          )
                        }
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}


export default DashboardPage
