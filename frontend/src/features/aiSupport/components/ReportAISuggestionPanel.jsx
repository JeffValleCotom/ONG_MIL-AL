import {
  useEffect,
  useState,
} from 'react'

import {
  createAIInsight,
  getAIInsight,
  getAIInsights,
  reviewAIInsight,
} from '../services/aiInsightService'

import './ReportAISuggestionPanel.css'


const REPORT_KIND = 'REPORT_SUGGESTION'


const STATUS_LABELS = {
  PENDING: 'Pendiente de revisión',
  ACCEPTED: 'Aceptado por profesional',
  DISCARDED: 'Descartado',
}


function getErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible completar la solicitud.'
    )
  }

  const fields = [
    'source_report_id',
    'student_id',
    'kind',
    'context',
    'decision',
    'detail',
  ]

  for (const field of fields) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible completar la solicitud.'
  )
}


function ReportSuggestionEditor({
  insight,
  context,
  onUpdated,
  onError,
}) {
  const initialSections = (
    insight.edited_content
      ?.suggested_sections
    || insight.result_json
      ?.suggested_sections
    || []
  )

  const [sections, setSections] = (
    useState(initialSections)
  )

  const [saving, setSaving] = (
    useState(false)
  )

  function updateDraft(
    index,
    value
  ) {
    setSections((current) => (
      current.map((item, itemIndex) => (
        itemIndex === index
          ? {
            ...item,
            draft_text: value,
          }
          : item
      ))
    ))
  }

  async function handleDecision(
    decision
  ) {
    if (saving) {
      return
    }

    setSaving(true)

    try {
      const updated = await reviewAIInsight(
        insight.id,
        {
          decision,
          edited_content: {
            suggested_sections: sections,
          },
        },
        context
      )

      onUpdated(updated)
    } catch (error) {
      onError(error)
    } finally {
      setSaving(false)
    }
  }

  const isPending = (
    insight.review_status === 'PENDING'
  )

  return (
    <div className="report-ai-editor">
      <div className="report-ai-notice">
        <strong>
          Contenido generado por IA
        </strong>

        <p>
          {insight.result_json?.ai_notice}
        </p>
      </div>

      <div className="report-ai-status">
        Estado:{' '}
        <strong>
          {STATUS_LABELS[
            insight.review_status
          ] || insight.review_status}
        </strong>
      </div>

      <section>
        <h4>Resumen de la sugerencia</h4>

        <p>
          {insight.result_json?.summary}
        </p>
      </section>

      <div className="report-ai-sections">
        {sections.map((item, index) => (
          <article
            className="report-ai-section"
            key={`${item.section}-${index}`}
          >
            <h4>
              {item.section}
            </h4>

            {item.rationale && (
              <p className="report-ai-rationale">
                {item.rationale}
              </p>
            )}

            <label>
              Contenido sugerido
              <textarea
                rows="6"
                value={item.draft_text || ''}
                disabled={!isPending}
                onChange={(event) => {
                  updateDraft(
                    index,
                    event.target.value
                  )
                }}
              />
            </label>
          </article>
        ))}
      </div>

      {isPending ? (
        <div className="report-ai-actions">
          <button
            className="button button--primary"
            type="button"
            disabled={saving}
            onClick={() => {
              handleDecision('ACCEPTED')
            }}
          >
            {saving
              ? 'Guardando...'
              : 'Aceptar contenido editado'}
          </button>

          <button
            className="button button--secondary"
            type="button"
            disabled={saving}
            onClick={() => {
              handleDecision('DISCARDED')
            }}
          >
            Descartar
          </button>
        </div>
      ) : (
        <p className="report-ai-decision-note">
          La decisión profesional ya fue
          registrada. El contenido original del
          reporte permanece sin modificaciones.
        </p>
      )}
    </div>
  )
}


export default function ReportAISuggestionPanel({
  report,
  context,
}) {
  const [items, setItems] = useState([])
  const [selected, setSelected] = (
    useState(null)
  )

  const [loading, setLoading] = (
    useState(true)
  )
  const [generating, setGenerating] = (
    useState(false)
  )
  const [openingId, setOpeningId] = (
    useState(null)
  )

  const [error, setError] = useState('')
  const [success, setSuccess] = (
    useState('')
  )

  async function loadItems() {
    const response = await getAIInsights({
      context,
      studentId: report.student.id,
      sourceReportId: report.id,
      kind: REPORT_KIND,
    })

    setItems(response.items || [])
  }

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)

      try {
        const response = await getAIInsights({
          context,
          studentId: report.student.id,
          sourceReportId: report.id,
          kind: REPORT_KIND,
        })

        if (!cancelled) {
          setItems(response.items || [])
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            getErrorMessage(loadError)
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      cancelled = true
    }
  }, [
    context,
    report.id,
    report.student.id,
  ])

  async function handleGenerate() {
    if (generating) {
      return
    }

    setGenerating(true)
    setError('')
    setSuccess('')

    try {
      const created = await createAIInsight(
        {
          kind: REPORT_KIND,
          source_report_id: report.id,
        },
        context
      )

      setSelected(created)

      setSuccess(
        'Las sugerencias para el reporte '
        + 'fueron generadas correctamente.'
      )

      await loadItems()
    } catch (generateError) {
      setError(
        getErrorMessage(generateError)
      )
    } finally {
      setGenerating(false)
    }
  }

  async function handleOpen(id) {
    if (openingId) {
      return
    }

    setOpeningId(id)
    setError('')
    setSuccess('')

    try {
      const detail = await getAIInsight(
        id,
        context
      )

      setSelected(detail)
    } catch (openError) {
      setError(
        getErrorMessage(openError)
      )
    } finally {
      setOpeningId(null)
    }
  }

  async function handleUpdated(updated) {
    setSelected(updated)

    setSuccess(
      updated.review_status === 'ACCEPTED'
        ? (
          'El contenido editado fue validado '
          + 'por el profesional.'
        )
        : (
          'La sugerencia fue descartada '
          + 'correctamente.'
        )
    )

    await loadItems()
  }

  return (
    <section className="report-ai-panel">
      <div className="report-ai-panel__header">
        <div>
          <h3>Asistencia IA para reporte</h3>

          <p>
            Genera contenido de apoyo utilizando
            exclusivamente la información del
            reporte abierto.
          </p>
        </div>

        <button
          className="button button--secondary"
          type="button"
          disabled={generating}
          onClick={handleGenerate}
        >
          {generating
            ? 'Generando...'
            : 'Generar sugerencias IA'}
        </button>
      </div>

      <p className="report-ai-warning">
        Las sugerencias se mantienen separadas
        de la información registrada y nunca se
        incorporan automáticamente.
      </p>

      {error && (
        <div
          className={
            'reports-message '
            + 'reports-message--error'
          }
          role="alert"
        >
          {error}
        </div>
      )}

      {success && (
        <div
          className={
            'reports-message '
            + 'reports-message--success'
          }
          role="status"
        >
          {success}
        </div>
      )}

      {selected && (
        <ReportSuggestionEditor
          key={selected.id}
          insight={selected}
          context={context}
          onUpdated={handleUpdated}
          onError={(reviewError) => {
            setError(
              getErrorMessage(reviewError)
            )
          }}
        />
      )}

      <div className="report-ai-history">
        <h4>Asistencias generadas</h4>

        {loading ? (
          <p>Cargando...</p>
        ) : items.length === 0 ? (
          <p>
            Todavía no existen sugerencias IA
            asociadas a este reporte.
          </p>
        ) : (
          items.map((item) => (
            <div
              className="report-ai-history__item"
              key={item.id}
            >
              <div>
                <strong>
                  Sugerencia para reporte
                </strong>

                <p>
                  Estado:{' '}
                  {STATUS_LABELS[
                    item.review_status
                  ] || item.review_status}
                </p>
              </div>

              <button
                className="button button--secondary"
                type="button"
                disabled={
                  openingId === item.id
                }
                onClick={() => {
                  handleOpen(item.id)
                }}
              >
                {openingId === item.id
                  ? 'Abriendo...'
                  : (
                    item.review_status
                    === 'PENDING'
                      ? 'Abrir y revisar'
                      : 'Abrir'
                  )}
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  )
}
