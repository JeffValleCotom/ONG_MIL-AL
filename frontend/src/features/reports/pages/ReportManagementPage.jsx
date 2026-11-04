import { useEffect, useState } from 'react'

import {
  REPORT_TYPE_LABELS,
  REPORT_TYPES_BY_CONTEXT,
} from '../reportTypes'
import './ReportManagementPage.css'
import Modal from '../../../components/Modal'
import '../../../components/Modal.css'
import {
  createReport,
  exportReport,
  getReport,
  getReports,
} from '../services/reportService'

const FIELD_LABELS = {
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
  activities: 'Actividades',
  progress_notes: 'Avances',
  evaluation_type: 'Tipo de evaluación',
  results: 'Resultados',
  professional_role: 'Rol profesional',
  status: 'Estado',
  responsible_role: 'Rol responsable',
  estimated_start_date: 'Inicio estimado',
  estimated_end_date: 'Fin estimado',
  progress: 'Avances',
  date: 'Fecha',
  responsible: 'Responsable',
  first_name: 'Nombres',
  last_name: 'Apellidos',
  institutional_code: 'Código institucional',
  date_of_birth: 'Fecha de nacimiento',
  admission_date: 'Fecha de ingreso',
  is_active: 'Estado del estudiante',
}


const SECTION_LABELS = {
  general: 'Información general',
  academic: 'Seguimiento académico',
  psychological: 'Seguimiento psicológico',
  therapy: 'Seguimiento terapéutico',
  evaluations: 'Evaluaciones',
  performed_interventions: 'Intervenciones realizadas',
  planned_interventions: 'Intervenciones planificadas',
}


function getReportErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible completar la operación.'
    )
  }

  const fieldOrder = [
    'student_id',
    'report_type',
    'date_from',
    'date_to',
    'detail',
    'non_field_errors',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (Array.isArray(value) && value.length > 0) {
      return value[0]
    }

    if (typeof value === 'string' && value) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible completar la operación.'
  )
}


function formatDate(value) {
  if (!value) {
    return '—'
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value
      .split('-')
      .map(Number)

    return new Intl.DateTimeFormat(
      'es-GT'
    ).format(
      new Date(year, month - 1, day)
    )
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


function formatStudent(student) {
  if (!student) {
    return 'Estudiante'
  }

  return (
    `${student.first_name} ${student.last_name} `
    + `(${student.institutional_code})`
  )
}


function formatPerson(person) {
  if (!person) {
    return '—'
  }

  const fullName = [
    person.first_name,
    person.last_name,
  ]
    .filter(Boolean)
    .join(' ')

  return fullName || person.username || '—'
}


function formatScalar(key, value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  if (
    key === 'date'
    || key.endsWith('_date')
  ) {
    return formatDate(value)
  }

  if (key === 'is_active') {
    return value ? 'Activo' : 'Inactivo'
  }

  if (key === 'responsible') {
    return formatPerson(value)
  }

  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No'
  }

  return String(value)
}


function ReportRecord({
  record,
  nested = false,
}) {
  const entries = Object.entries(
    record ?? {}
  ).filter(([key]) => key !== 'id')

  return (
    <article
      className={
        nested
          ? 'reports-record reports-record--nested'
          : 'reports-record'
      }
    >
      {entries.map(([key, value]) => {
        if (
          Array.isArray(value)
          && value.length > 0
        ) {
          return (
            <div
              className="reports-record__nested"
              key={key}
            >
              <strong>
                {
                  key === 'followups'
                    ? 'Historial de seguimientos'
                    : FIELD_LABELS[key] || key
                }
              </strong>

              <div className="reports-record__nested-list">
                {value.map((nestedRecord, index) => (
                  <ReportRecord
                    key={
                      nestedRecord?.id
                      ?? `${key}-${index}`
                    }
                    record={nestedRecord}
                    nested
                  />
                ))}
              </div>
            </div>
          )
        }

        if (
          value
          && typeof value === 'object'
          && !Array.isArray(value)
        ) {
          return (
            <div
              className="reports-record__field"
              key={key}
            >
              <strong>
                {FIELD_LABELS[key] || key}
              </strong>

              <span>
                {formatPerson(value)}
              </span>
            </div>
          )
        }

        return (
          <div
            className="reports-record__field"
            key={key}
          >
            <strong>
              {FIELD_LABELS[key] || key}
            </strong>

            <span>
              {formatScalar(key, value)}
            </span>
          </div>
        )
      })}
    </article>
  )
}


function ReportViewer({ report }) {

  const snapshot =
    report.content_snapshot ?? {}

  const sections =
    snapshot.sections ?? {}

  return (
    <div className="reports-viewer">
      <div className="reports-viewer__header">
        <div>
          <p className="reports-page__eyebrow">
            Reporte generado
          </p>

          <h2>
            {
              REPORT_TYPE_LABELS[
                report.report_type
              ] ?? report.report_type
            }
          </h2>

          <p>
            {formatStudent(report.student)}
          </p>
        </div>

        <div className="reports-viewer__metadata">
          <span>
            Generado: {formatDate(report.generated_at)}
          </span>

          <span>
            Contexto: {report.generated_role}
          </span>

          <span>
            Período:{' '}
            {
              report.date_from
                ? formatDate(report.date_from)
                : 'Sin fecha inicial'
            }
            {' — '}
            {
              report.date_to
                ? formatDate(report.date_to)
                : 'Sin fecha final'
            }
          </span>
        </div>
      </div>

      {snapshot.summary && (
        <section className="reports-summary">
          <h3>Resumen</h3>

          <div className="reports-summary__grid">
            {Object.entries(
              snapshot.summary
            )
              .filter(
                ([key]) => key !== 'highlights'
              )
              .map(([key, value]) => (
                <div
                  className="reports-summary__item"
                  key={key}
                >
                  <strong>
                    {
                      key
                        .replaceAll('_', ' ')
                    }
                  </strong>

                  <span>{value}</span>
                </div>
              ))}
          </div>

          {
            Array.isArray(
              snapshot.summary.highlights
            )
            && snapshot.summary.highlights.length > 0
            && (
              <div className="reports-highlights">
                <h4>Principales avances</h4>

                <ul>
                  {snapshot.summary.highlights.map(
                    (highlight, index) => (
                      <li
                        key={
                          `${highlight.area}-${index}`
                        }
                      >
                        <strong>
                          {highlight.area}:
                        </strong>{' '}
                        {highlight.text}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )
          }
        </section>
      )}

      <div className="reports-sections">
        {Object.entries(sections).map(
          ([sectionName, content]) => (
            <section
              className="reports-section"
              key={sectionName}
            >
              <h3>
                {
                  SECTION_LABELS[sectionName]
                  ?? sectionName
                }
              </h3>

              {
                Array.isArray(content)
                  ? (
                      content.length > 0
                        ? (
                            <div className="reports-section__records">
                              {content.map(
                                (record, index) => (
                                  <ReportRecord
                                    key={
                                      record?.id
                                      ?? (
                                        `${sectionName}-${index}`
                                      )
                                    }
                                    record={record}
                                  />
                                )
                              )}
                            </div>
                          )
                        : (
                            <p className="reports-empty">
                              No hay registros en este período.
                            </p>
                          )
                    )
                  : (
                      <ReportRecord
                        record={content}
                      />
                    )
              }
            </section>
          )
        )}
      </div>
    </div>
  )
}


function ReportManagementPage({
  students,
  studentContext,
  onBack,
  onLogout,
  onChangeSpace,
}) {
  const availableTypes =
    REPORT_TYPES_BY_CONTEXT[
      studentContext
    ] ?? []

  const [reports, setReports] =
    useState([])

  const [openedReport, setOpenedReport] =
    useState(null)

  const [isLoading, setIsLoading] =
    useState(true)

  const [isGenerating, setIsGenerating] =
    useState(false)

  const [listError, setListError] =
    useState('')

  const [generationError, setGenerationError] =
    useState('')

  const [success, setSuccess] =
    useState('')

  const [openingReportId, setOpeningReportId] =
    useState(null)

  const [openError, setOpenError] =
    useState('')

  const [isExporting, setIsExporting] =
    useState(false)

  const [exportError, setExportError] =
    useState('')

  const [generationForm, setGenerationForm] =
    useState({
      studentId: '',
      reportType: '',
      dateFrom: '',
      dateTo: '',
    })

  const [filterForm, setFilterForm] =
    useState({
      studentId: '',
      reportType: '',
      dateFrom: '',
      dateTo: '',
    })

  useEffect(() => {
    let isMounted = true

    async function loadInitialReports() {
      setIsLoading(true)
      setListError('')

      try {
        const response = await getReports({
          context: studentContext,
        })

        if (isMounted) {
          setReports(response.items ?? [])
        }
      } catch (error) {
        if (isMounted) {
          setListError(
            getReportErrorMessage(error)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadInitialReports()

    return () => {
      isMounted = false
    }
  }, [studentContext])

    async function loadReports(filters) {
      setIsLoading(true)
      setListError('')

      try {
        const response = await getReports({
          context: studentContext,
          studentId: filters.studentId,
          reportType: filters.reportType,
          dateFrom: filters.dateFrom,
          dateTo: filters.dateTo,
        })

        setReports(response.items ?? [])
      } catch (error) {
        setListError(
          getReportErrorMessage(error)
        )
      } finally {
        setIsLoading(false)
      }
      }

    async function handleOpenReport(report) {
      if (openingReportId) {
        return
      }

      setOpeningReportId(report.id)
      setOpenError('')
      setExportError('')
      setOpenedReport(null)

      try {
        const detail = await getReport(
          report.id,
          studentContext
        )

        setOpenedReport(detail)
      } catch (error) {
        setOpenError(
          getReportErrorMessage(error)
        )
      } finally {
        setOpeningReportId(null)
      }
    }

  function handleGenerationChange(event) {
    const { name, value } = event.target

    setGenerationForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  function handleFilterChange(event) {
    const { name, value } = event.target

    setFilterForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleGenerate(event) {
    event.preventDefault()

    if (isGenerating) {
      return
    }

    const studentId =
      generationForm.studentId
      || students[0]?.id
      || ''

    const reportType =
      generationForm.reportType
      || availableTypes[0]
      || ''

    if (!studentId || !reportType) {
      setGenerationError(
        'Selecciona un estudiante y un tipo de reporte.'
      )
      return
    }

    setIsGenerating(true)
    setGenerationError('')
    setSuccess('')

    try {
      const report = await createReport(
        {
          student_id: Number(studentId),
          report_type: reportType,
          date_from:
            generationForm.dateFrom || null,
          date_to:
            generationForm.dateTo || null,
        },
        studentContext
      )

      setReports((current) => [
        report,
        ...current.filter(
          (item) => item.id !== report.id
        ),
      ])

      setSuccess(
        'Reporte generado correctamente.'
        + 'Puedes abrirlo desde la lista de reportes.'
      )
    } catch (error) {
      setGenerationError(
        getReportErrorMessage(error)
      )
    } finally {
      setIsGenerating(false)
    }
  }

    async function handleExportReport() {
      if (
        !openedReport
        || isExporting
      ) {
        return
      }

      setIsExporting(true)
      setExportError('')

      try {
        const blob = await exportReport(
          openedReport.id,
          studentContext
        )

        const url = URL.createObjectURL(blob)

        const link = document.createElement('a')

        link.href = url
        link.download = (
          `reporte-${openedReport.report_type.toLowerCase()}-`
          + `${openedReport.student.institutional_code}-`
          + `${openedReport.id}.pdf`
        )

        document.body.appendChild(link)
        link.click()
        link.remove()

        setTimeout(() => {
          URL.revokeObjectURL(url)
        }, 0)
      } catch (error) {
        setExportError(
          getReportErrorMessage(error)
        )
      } finally {
        setIsExporting(false)
      }
    }

  function handleFilterSubmit(event) {
    event.preventDefault()

    loadReports(filterForm)
  }

  function handleClearFilters() {
    const emptyFilters = {
      studentId: '',
      reportType: '',
      dateFrom: '',
      dateTo: '',
    }

    setFilterForm(emptyFilters)
    loadReports(emptyFilters)
  }

  const resolvedStudentId =
    generationForm.studentId
    || students[0]?.id
    || ''

  const resolvedReportType =
    generationForm.reportType
    || availableTypes[0]
    || ''

  return (
    <main className="reports-page">
      <header className="reports-page__header">
        <div>
          <p className="reports-page__eyebrow">
            Reportes MIL-AL
          </p>

          <h1>
            Generación y consulta de reportes
          </h1>

          <p className="reports-page__description">
            Genera, consulta y analiza reportes de
            seguimiento de los estudiantes autorizados.
          </p>
        </div>

        <div className="reports-page__actions">
          <button
            className="button button--secondary"
            type="button"
            onClick={onBack}
          >
            Volver a estudiantes
          </button>

          {onChangeSpace && (
            <button
              className="button button--secondary"
              type="button"
              onClick={onChangeSpace}
            >
              Cambiar espacio
            </button>
          )}

          <button
            className="button button--secondary"
            type="button"
            onClick={onLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      {success && (
        <div
          className="reports-message reports-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      <section className="reports-card">
        <div className="reports-card__header">
          <h2>Generar reporte</h2>

          <p>
            Selecciona estudiante, tipo y período de
            información.
          </p>
        </div>

        <form
          className="reports-form"
          onSubmit={handleGenerate}
        >
          <div className="reports-field">
            <label htmlFor="report-student">
              Estudiante
            </label>

            <select
              id="report-student"
              name="studentId"
              value={resolvedStudentId}
              onChange={handleGenerationChange}
              disabled={isGenerating}
            >
              {students.length === 0 && (
                <option value="">
                  No hay estudiantes disponibles
                </option>
              )}

              {students.map((student) => (
                <option
                  key={student.id}
                  value={student.id}
                >
                  {formatStudent(student)}
                </option>
              ))}
            </select>
          </div>

          <div className="reports-field">
            <label htmlFor="report-type">
              Tipo de reporte
            </label>

            <select
              id="report-type"
              name="reportType"
              value={resolvedReportType}
              onChange={handleGenerationChange}
              disabled={isGenerating}
            >
              {availableTypes.map((type) => (
                <option
                  key={type}
                  value={type}
                >
                  {REPORT_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
          </div>

          <div className="reports-field">
            <label htmlFor="report-date-from">
              Fecha desde
            </label>

            <input
              id="report-date-from"
              name="dateFrom"
              type="date"
              value={generationForm.dateFrom}
              onChange={handleGenerationChange}
              disabled={isGenerating}
            />
          </div>

          <div className="reports-field">
            <label htmlFor="report-date-to">
              Fecha hasta
            </label>

            <input
              id="report-date-to"
              name="dateTo"
              type="date"
              value={generationForm.dateTo}
              onChange={handleGenerationChange}
              disabled={isGenerating}
            />
          </div>

          <div className="reports-form__actions">
            <button
              className="button button--primary"
              type="submit"
              disabled={
                isGenerating
                || students.length === 0
              }
            >
              {
                isGenerating
                  ? 'Generando...'
                  : 'Generar reporte'
              }
            </button>
          </div>
        </form>

        {generationError && (
          <div
            className="reports-message reports-message--error"
            role="alert"
          >
            {generationError}
          </div>
        )}
      </section>

      <section className="reports-card">
        <div className="reports-card__header">
          <h2>Reportes generados</h2>

          <p>
            Filtra los reportes históricos disponibles en
            tu contexto autorizado.
          </p>
        </div>

        <form
          className="reports-form"
          onSubmit={handleFilterSubmit}
        >
          <div className="reports-field">
            <label htmlFor="filter-student">
              Estudiante
            </label>

            <select
              id="filter-student"
              name="studentId"
              value={filterForm.studentId}
              onChange={handleFilterChange}
            >
              <option value="">
                Todos
              </option>

              {students.map((student) => (
                <option
                  key={student.id}
                  value={student.id}
                >
                  {formatStudent(student)}
                </option>
              ))}
            </select>
          </div>

          <div className="reports-field">
            <label htmlFor="filter-report-type">
              Tipo
            </label>

            <select
              id="filter-report-type"
              name="reportType"
              value={filterForm.reportType}
              onChange={handleFilterChange}
            >
              <option value="">
                Todos
              </option>

              {availableTypes.map((type) => (
                <option
                  key={type}
                  value={type}
                >
                  {REPORT_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
          </div>

          <div className="reports-field">
            <label htmlFor="filter-date-from">
              Generado desde
            </label>

            <input
              id="filter-date-from"
              name="dateFrom"
              type="date"
              value={filterForm.dateFrom}
              onChange={handleFilterChange}
            />
          </div>

          <div className="reports-field">
            <label htmlFor="filter-date-to">
              Generado hasta
            </label>

            <input
              id="filter-date-to"
              name="dateTo"
              type="date"
              value={filterForm.dateTo}
              onChange={handleFilterChange}
            />
          </div>

          <div className="reports-form__actions">
            <button
              className="button button--primary"
              type="submit"
            >
              Filtrar
            </button>

            <button
              className="button button--secondary"
              type="button"
              onClick={handleClearFilters}
            >
              Limpiar
            </button>
          </div>
        </form>

        {listError && (
          <div
            className="reports-message reports-message--error"
            role="alert"
          >
            {listError}
          </div>
        )}

        {isLoading && (
          <div className="reports-empty">
            Cargando reportes...
          </div>
        )}

        {!isLoading && !listError && reports.length === 0 && (
          <div className="reports-empty">
            No hay reportes generados con estos filtros.
          </div>
        )}

        {!isLoading && reports.length > 0 && (
          <div className="reports-list">
            {reports.map((report) => (
              <article
                className="reports-list__item"
                key={report.id}
              >
                <div>
                  <strong>
                    {
                      REPORT_TYPE_LABELS[
                        report.report_type
                      ] ?? report.report_type
                    }
                  </strong>

                  <p>
                    {formatStudent(report.student)}
                  </p>

                  <span>
                    Generado: {formatDate(report.generated_at)}
                  </span>

                  <span>
                    {' · '}
                    Contexto: {report.generated_role}
                  </span>
                </div>

                <button
                  className="button button--secondary"
                  type="button"
                  onClick={() => {
                    handleOpenReport(report)
                  }}
                  disabled={openingReportId !== null}
                >
                  {
                    openingReportId === report.id
                      ? 'Abriendo...'
                      : 'Abrir reporte'
                  }
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

            {openError && (
              <div
                className="reports-message reports-message--error"
                role="alert"
              >
                {openError}
              </div>
            )}

            {openedReport && (
              <Modal
                title={
                  REPORT_TYPE_LABELS[
                    openedReport.report_type
                  ] ?? 'Reporte'
                }
                onClose={() => {
                  if (!isExporting) {
                    setOpenedReport(null)
                    setExportError('')
                  }
                }}
              >
                <ReportViewer
                  report={openedReport}
                />

                {exportError && (
                  <div
                    className="reports-message reports-message--error"
                    role="alert"
                  >
                    {exportError}
                  </div>
                )}

                <div className="reports-document__actions">
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={handleExportReport}
                    disabled={isExporting}
                  >
                    {
                      isExporting
                        ? 'Exportando...'
                        : 'Exportar PDF'
                    }
                  </button>

                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => {
                      setOpenedReport(null)
                      setExportError('')
                    }}
                    disabled={isExporting}
                  >
                    Cerrar
                  </button>
                </div>
              </Modal>
            )}
    </main>
  )
}


export default ReportManagementPage
