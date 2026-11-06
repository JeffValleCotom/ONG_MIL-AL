import { useEffect, useMemo, useState } from 'react'

import StudentEvolutionPanel
  from '../../students/components/StudentEvolutionPanel'
import {
  getStudentRecord,
  getStudents,
} from '../../students/services/studentService'
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


const INDIVIDUAL_AREAS_BY_CONTEXT = {
  DOCENTE: [
    'academic',
    'evaluations',
  ],
  PSICOLOGO: [
    'psychological',
    'evaluations',
    'interventions',
  ],
  TERAPEUTA: [
    'therapy',
    'evaluations',
    'interventions',
  ],
  RESPONSABLE_INSTITUCIONAL: [],
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


function getStudentName(student) {
  if (!student) {
    return ''
  }

  return [
    student.first_name,
    student.last_name,
  ]
    .filter(Boolean)
    .join(' ')
}


function buildIndividualMetrics(record) {
  const evolution =
    record?.sections?.evolution

  const periods =
    evolution?.periods ?? []

  const records = periods.flatMap(
    (period) => period.records ?? []
  )

  const countRecordType = (recordType) => (
    records.filter(
      (item) => item.record_type === recordType
    ).length
  )

  const interventionSection =
    record?.sections?.interventions

  const plans =
    interventionSection?.planned ?? []

  const performed =
    interventionSection?.performed ?? []

  const interventionFollowUps = plans.reduce(
    (total, plan) => (
      total + (plan.followups?.length ?? 0)
    ),
    0
  )

  return {
    totalRecords:
      evolution?.summary?.total_records ?? 0,

    followUps:
      evolution?.summary?.followup_count ?? 0,

    evaluations:
      evolution?.summary?.evaluation_count ?? 0,

    periods:
      evolution?.summary?.period_count ?? 0,

    academic: countRecordType(
      'ACADEMIC_FOLLOWUP'
    ),

    psychological: countRecordType(
      'PSYCHOLOGICAL_FOLLOWUP'
    ),

    therapy: countRecordType(
      'THERAPY_FOLLOWUP'
    ),

    interventionActivity:
      plans.length
      + performed.length
      + interventionFollowUps,

    interventionPlans: plans.length,

    interventionPerformed: performed.length,

    interventionFollowUps,

    interventionPlanned: plans.filter(
      (plan) => plan.status === 'PLANNED'
    ).length,

    interventionInProgress: plans.filter(
      (plan) => plan.status === 'IN_PROGRESS'
    ).length,

    interventionCompleted: plans.filter(
      (plan) => plan.status === 'COMPLETED'
    ).length,

    interventionCancelled: plans.filter(
      (plan) => plan.status === 'CANCELLED'
    ).length,
  }
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
  const [
    activeView,
    setActiveView,
  ] = useState('general')

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

  const [
    individualStudents,
    setIndividualStudents,
  ] = useState([])

  const [
    selectedStudentId,
    setSelectedStudentId,
  ] = useState('')

  const [
    individualRecord,
    setIndividualRecord,
  ] = useState(null)

  const [
    isLoadingStudents,
    setIsLoadingStudents,
  ] = useState(false)

  const [
    isLoadingIndividual,
    setIsLoadingIndividual,
  ] = useState(false)

  const [
    individualError,
    setIndividualError,
  ] = useState('')

  useEffect(() => {
    if (activeView !== 'general') {
      return undefined
    }

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
    activeView,
    filters,
    studentContext,
  ])

  useEffect(() => {
    if (activeView !== 'individual') {
      return undefined
    }

    let isMounted = true

    async function loadStudents() {
      setIsLoadingStudents(true)
      setIndividualError('')

      try {
        const response = await getStudents({
          context: studentContext,
        })

        const studentItems = Array.isArray(response)
          ? response
          : response?.results ?? []

        if (isMounted) {
          setIndividualStudents(studentItems)

          setSelectedStudentId((current) => {
            const stillExists = studentItems.some(
              (student) => (
                String(student.id)
                === String(current)
              )
            )

            return stillExists
              ? current
              : ''
          })
        }
      } catch (loadError) {
        if (isMounted) {
          setIndividualStudents([])
          setIndividualError(
            getDashboardErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoadingStudents(false)
        }
      }
    }

    loadStudents()

    return () => {
      isMounted = false
    }
  }, [
    activeView,
    studentContext,
  ])

  useEffect(() => {
    if (
      activeView !== 'individual'
      || !selectedStudentId
    ) {
      return undefined
    }

    let isMounted = true

    async function loadIndividualRecord() {
      setIsLoadingIndividual(true)
      setIndividualError('')
      setIndividualRecord(null)

      try {
        const record = await getStudentRecord(
          selectedStudentId,
          studentContext
        )

        if (isMounted) {
          setIndividualRecord(record)
        }
      } catch (loadError) {
        if (isMounted) {
          setIndividualError(
            getDashboardErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoadingIndividual(false)
        }
      }
    }

    loadIndividualRecord()

    return () => {
      isMounted = false
    }
  }, [
    activeView,
    selectedStudentId,
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

  const selectedStudent = useMemo(
    () => (
      individualStudents.find(
        (student) => (
          String(student.id)
          === String(selectedStudentId)
        )
      ) ?? null
    ),
    [
      individualStudents,
      selectedStudentId,
    ]
  )

  const individualMetrics = useMemo(
    () => buildIndividualMetrics(
      individualRecord
    ),
    [individualRecord]
  )

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

  const individualAreas =
    INDIVIDUAL_AREAS_BY_CONTEXT[
      studentContext
    ] ?? []

  const individualEvolution =
    individualRecord?.sections?.evolution

  const individualInterventions =
    individualRecord?.sections?.interventions

  return (
    <main className="dashboard-page">
      <section className="dashboard-view-switch">
        <div>
          <p className="dashboard-eyebrow">
            Visualización
          </p>

          <h2>
            Panel de seguimiento
          </h2>

          <p>
            Consulta indicadores consolidados
            o el progreso de un estudiante.
          </p>
        </div>

        <div
          className="dashboard-view-switch__tabs"
          role="tablist"
          aria-label="Tipo de dashboard"
        >
          <button
            className={
              'dashboard-view-switch__tab'
              + (
                activeView === 'general'
                  ? ' dashboard-view-switch__tab--active'
                  : ''
              )
            }
            type="button"
            role="tab"
            aria-selected={
              activeView === 'general'
            }
            onClick={() => {
              setActiveView('general')
            }}
          >
            General
          </button>

          <button
            className={
              'dashboard-view-switch__tab'
              + (
                activeView === 'individual'
                  ? ' dashboard-view-switch__tab--active'
                  : ''
              )
            }
            type="button"
            role="tab"
            aria-selected={
              activeView === 'individual'
            }
            onClick={() => {
              setActiveView('individual')
            }}
          >
            Individual
          </button>
        </div>
      </section>

      {activeView === 'general' && (
        <>
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
                  className={
                    'milal-button '
                    + 'milal-button--primary'
                  }
                  type="submit"
                >
                  Aplicar
                </button>

                <button
                  className={
                    'milal-button '
                    + 'milal-button--secondary'
                  }
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
              className={
                'dashboard-message '
                + 'dashboard-message--error'
              }
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
                  detail={
                    'Según tu contexto '
                    + 'profesional'
                  }
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
                    filters.dateFrom
                    || filters.dateTo
                      ? 'Periodo seleccionado'
                      : (
                        'Todo el historial '
                        + 'disponible'
                      )
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
                        {
                          AREA_LABELS[area]
                          ?? area
                        }
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
                        Seguimiento de las
                        planificaciones registradas
                        en el periodo.
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
                        interventionIndicators
                          .in_progress
                      }
                      label="En progreso"
                      tone="primary"
                    />

                    <DashboardStat
                      value={
                        interventionIndicators
                          .completed
                      }
                      label="Completadas"
                      tone="success"
                    />

                    <DashboardStat
                      value={
                        interventionIndicators
                          .cancelled
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

                  {
                    interventionIndicators
                      .direct_records > 0
                    && (
                      <p className="dashboard-legacy-note">
                        También existen{' '}
                        <strong>
                          {
                            interventionIndicators
                              .direct_records
                          }
                        </strong>{' '}
                        registros directos históricos
                        de intervenciones.
                      </p>
                    )
                  }
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
                      Distribución de registros por
                      mes y área de seguimiento.
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
                    {dashboard.timeline.map(
                      (period) => (
                        <article
                          className="dashboard-period"
                          key={period.period}
                        >
                          <div
                            className={
                              'dashboard-period__label'
                            }
                          >
                            {
                              formatPeriod(
                                period.period
                              )
                            }
                          </div>

                          <div
                            className={
                              'dashboard-period__areas'
                            }
                          >
                            {
                              dashboard.visible_areas
                                .map(
                                  (area) => {
                                    const value =
                                      period[area] ?? 0

                                    const width =
                                      timelineMax > 0
                                        ? (
                                          value
                                          / timelineMax
                                          * 100
                                        )
                                        : 0

                                    return (
                                      <div
                                        className={
                                          'dashboard-period'
                                          + '__area'
                                        }
                                        key={area}
                                      >
                                        <div
                                          className={
                                            'dashboard-period'
                                            + '__area-label'
                                          }
                                        >
                                          <span>
                                            {
                                              AREA_LABELS[
                                                area
                                              ]
                                              ?? area
                                            }
                                          </span>

                                          <strong>
                                            {value}
                                          </strong>
                                        </div>

                                        <div
                                          className={
                                            'dashboard-bar'
                                          }
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
                                )
                            }
                          </div>
                        </article>
                      )
                    )}
                  </div>
                )}
              </section>
            </>
          )}
        </>
      )}

      {activeView === 'individual' && (
        <>
          <section className="dashboard-filter-card">
            <div className="dashboard-filter-card__heading">
              <div>
                <p className="dashboard-eyebrow">
                  Dashboard individual
                </p>

                <h2>
                  Selecciona un estudiante
                </h2>

                <p>
                  Solo se muestran estudiantes
                  disponibles dentro de tu contexto
                  autorizado.
                </p>
              </div>
            </div>

            <div className="dashboard-individual-selector">
              <div className="dashboard-field">
                <label htmlFor="dashboard-student">
                  Estudiante
                </label>

                <select
                  id="dashboard-student"
                  value={selectedStudentId}
                  disabled={isLoadingStudents}
                  onChange={(event) => {
                    setIndividualRecord(null)
                    setIndividualError('')
                    setSelectedStudentId(
                      event.target.value
                    )
                  }}
                >
                  <option value="">
                    {isLoadingStudents
                      ? 'Cargando estudiantes...'
                      : 'Selecciona un estudiante'}
                  </option>

                  {individualStudents.map(
                    (student) => (
                      <option
                        key={student.id}
                        value={student.id}
                      >
                        {getStudentName(student)}
                        {' · '}
                        {student.institutional_code}
                      </option>
                    )
                  )}
                </select>
              </div>
            </div>
          </section>

          {individualError && (
            <div
              className={
                'dashboard-message '
                + 'dashboard-message--error'
              }
              role="alert"
            >
              {individualError}
            </div>
          )}

          {!isLoadingStudents
            && individualStudents.length === 0
            && !individualError && (
              <div className="dashboard-empty">
                No hay estudiantes disponibles
                dentro de este contexto.
              </div>
          )}

          {selectedStudent
            && isLoadingIndividual && (
              <section className="dashboard-loading">
                Cargando seguimiento individual...
              </section>
          )}

          {selectedStudent
            && individualRecord
            && !isLoadingIndividual && (
              <>
                <section className="dashboard-individual-hero">
                  <div>
                    <p className="dashboard-eyebrow">
                      Seguimiento individual
                    </p>

                    <h2>
                      {getStudentName(
                        selectedStudent
                      )}
                    </h2>

                    <p>
                      {
                        selectedStudent
                          .institutional_code
                      }
                      {' · '}
                      {
                        selectedStudent.is_active
                          ? 'Estudiante activo'
                          : 'Estudiante inactivo'
                      }
                    </p>
                  </div>

                  <span
                    className={
                      'dashboard-individual-status '
                      + (
                        selectedStudent.is_active
                          ? (
                            'dashboard-individual-status'
                            + '--active'
                          )
                          : (
                            'dashboard-individual-status'
                            + '--inactive'
                          )
                      )
                    }
                  >
                    {
                      selectedStudent.is_active
                        ? 'Activo'
                        : 'Inactivo'
                    }
                  </span>
                </section>

                <section
                  className="dashboard-summary"
                  aria-label={
                    'Resumen individual '
                    + 'del estudiante'
                  }
                >
                  <DashboardStat
                    value={
                      individualMetrics.totalRecords
                    }
                    label="Registros"
                    detail="Seguimiento disponible"
                    tone="primary"
                  />

                  <DashboardStat
                    value={
                      individualMetrics.followUps
                    }
                    label="Seguimientos"
                    detail="Registros profesionales"
                  />

                  <DashboardStat
                    value={
                      individualMetrics.evaluations
                    }
                    label="Evaluaciones"
                    detail="Evaluaciones registradas"
                  />

                  <DashboardStat
                    value={
                      individualMetrics.periods
                    }
                    label="Periodos con actividad"
                    detail="Historial disponible"
                    tone="success"
                  />
                </section>

                <section className="dashboard-section">
                  <div className="dashboard-section__heading">
                    <div>
                      <p className="dashboard-eyebrow">
                        Áreas
                      </p>

                      <h2>
                        Seguimiento disponible
                      </h2>

                      <p>
                        Información visible de acuerdo
                        con tu contexto y permisos.
                      </p>
                    </div>
                  </div>

                  {individualAreas.length === 0 ? (
                    <div className="dashboard-empty">
                      El contexto institucional permite
                      consultar el resumen del
                      estudiante, pero no expone
                      seguimientos profesionales
                      sensibles en esta vista.
                    </div>
                  ) : (
                    <div className="dashboard-indicators">
                      {individualAreas.map((area) => {
                        const value = (
                          area === 'evaluations'
                            ? individualMetrics.evaluations
                            : area === 'interventions'
                              ? individualMetrics.interventionActivity
                              : individualMetrics[area] ?? 0
                        )
                        return (
                          <article
                            className={
                              'dashboard-indicator'
                            }
                            key={area}
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

                            <small>
                              registros disponibles
                            </small>
                          </article>
                        )
                      })}
                    </div>
                  )}
                </section>

                {individualInterventions && (
                  <section className="dashboard-section">
                    <div className="dashboard-section__heading">
                      <div>
                        <p className="dashboard-eyebrow">
                          Intervenciones
                        </p>

                        <h2>
                          Seguimiento de intervenciones
                        </h2>

                        <p>
                          Estado actual de los planes y
                          avances autorizados.
                        </p>
                      </div>
                    </div>

                    <div className="dashboard-interventions">
                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionPlans
                        }
                        label="Planes"
                      />

                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionPlanned
                        }
                        label="Planificadas"
                      />

                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionInProgress
                        }
                        label="En progreso"
                        tone="primary"
                      />

                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionCompleted
                        }
                        label="Completadas"
                        tone="success"
                      />

                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionFollowUps
                        }
                        label="Avances"
                      />

                      <DashboardStat
                        value={
                          individualMetrics
                            .interventionPerformed
                        }
                        label="Registros directos"
                      />
                    </div>
                  </section>
                )}

                <section className="dashboard-section">
                  <div className="dashboard-section__heading">
                    <div>
                      <p className="dashboard-eyebrow">
                        Evolución
                      </p>

                      <h2>
                        Evolución y progreso
                      </h2>

                      <p>
                        Revisa la actividad registrada
                        y compara periodos de
                        seguimiento.
                      </p>
                    </div>
                  </div>

                  {individualEvolution ? (
                    <div className="dashboard-individual-evolution">
                      <StudentEvolutionPanel
                        evolution={
                          individualEvolution
                        }
                      />
                    </div>
                  ) : (
                    <div className="dashboard-empty">
                      No hay información de evolución
                      disponible para este contexto.
                    </div>
                  )}
                </section>
              </>
          )}

          {!selectedStudentId
            && !isLoadingStudents
            && individualStudents.length > 0 && (
              <div className="dashboard-empty">
                Selecciona un estudiante para
                visualizar su dashboard individual.
              </div>
          )}
        </>
      )}
    </main>
  )
}


export default DashboardPage
