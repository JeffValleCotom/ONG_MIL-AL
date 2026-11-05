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

import './AIInsightPanel.css'


const MODE_CONFIG = {
  ANALYSIS: {
    label: 'Análisis',
    title: 'Análisis inteligente',
    action: 'Generar análisis inteligente',
    loadingAction: 'Analizando información...',
  },
  FOLLOWUP_SUGGESTION: {
    label: 'Sugerencias',
    title: 'Sugerencias de seguimiento',
    action: 'Generar sugerencias',
    loadingAction: 'Generando sugerencias...',
  },
  INTERVENTION_RECOMMENDATION: {
    label: 'Recomendaciones',
    title: 'Recomendaciones de intervención',
    action: 'Generar recomendaciones',
    loadingAction: 'Generando recomendaciones...',
  },
  HISTORY: {
    label: 'Historial',
    title: 'Historial de asistencia IA',
  },
}


const REVIEW_STATUS_LABELS = {
  NOT_APPLICABLE: 'No aplica',
  PENDING: 'Pendiente de revisión',
  ACCEPTED: 'Aceptada',
  DISCARDED: 'Descartada',
  IGNORED: 'Ignorada',
}


function formatDate(value) {
  if (!value) {
    return 'Sin límite'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}/${month}/${year}`
}


function formatDateTime(value) {
  if (!value) {
    return ''
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    }
  ).format(
    new Date(value)
  )
}


function getAIErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible completar la solicitud.'
    )
  }

  const fieldOrder = [
    'student_id',
    'kind',
    'decision',
    'date_from',
    'date_to',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
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


function AnalysisItems({
  title,
  items,
  emptyMessage,
}) {
  return (
    <section className="ai-insight-result-section">
      <h4>{title}</h4>

      {items?.length ? (
        <div className="ai-insight-observation-list">
          {items.map((item, index) => (
            <article
              className="ai-insight-observation"
              key={`${item.area}-${index}`}
            >
              <strong>
                {item.area || 'General'}
              </strong>

              <p>
                {item.observation}
              </p>

              {item.evidence?.length > 0 && (
                <div>
                  <span className="ai-insight-evidence-title">
                    Evidencia relacionada
                  </span>

                  <ul>
                    {item.evidence.map(
                      (evidence, evidenceIndex) => (
                        <li
                          key={
                            `${evidence}-${evidenceIndex}`
                          }
                        >
                          {evidence}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </article>
          ))}
        </div>
      ) : (
        <p className="ai-insight-empty">
          {emptyMessage}
        </p>
      )}
    </section>
  )
}


function ContextSection({
  insight,
  showContext,
  onToggleContext,
}) {
  return (
    <>
      <div className="ai-insight-context-actions">
        <button
          className="button button--secondary"
          type="button"
          onClick={onToggleContext}
        >
          {showContext
            ? 'Ocultar información utilizada'
            : 'Ver información utilizada'}
        </button>
      </div>

      {showContext && (
        <section className="ai-insight-context">
          <div className="ai-insight-context__header">
            <div>
              <h4>
                Información utilizada por la IA
              </h4>

              <p>
                Contexto autorizado utilizado para
                generar este contenido.
              </p>
            </div>
          </div>

          <pre>
            {JSON.stringify(
              insight.context_snapshot,
              null,
              2
            )}
          </pre>
        </section>
      )}
    </>
  )
}


function AnalysisDetail({
  insight,
  showContext,
  onToggleContext,
}) {
  const result = insight.result_json || {}

  return (
    <div className="ai-insight-detail">
      <div className="ai-insight-notice">
        <strong>
          Contenido generado por IA
        </strong>

        <p>
          {result.ai_notice}
        </p>
      </div>

      <section className="ai-insight-summary">
        <h4>Resumen</h4>

        <p>
          {result.summary
            || 'No se generó un resumen.'}
        </p>
      </section>

      <AnalysisItems
        title="Tendencias identificadas"
        items={result.trends}
        emptyMessage={
          'No se identificaron tendencias '
          + 'con la información disponible.'
        }
      />

      <AnalysisItems
        title="Avances observados"
        items={result.progress}
        emptyMessage={
          'No se identificaron avances '
          + 'suficientemente respaldados.'
        }
      />

      <AnalysisItems
        title="Aspectos que requieren atención"
        items={result.attention_points}
        emptyMessage={
          'No se identificaron aspectos '
          + 'adicionales que requieran atención.'
        }
      />

      <ContextSection
        insight={insight}
        showContext={showContext}
        onToggleContext={onToggleContext}
      />
    </div>
  )
}


function SuggestionDetail({
  insight,
}) {
  const result = insight.result_json || {}

  return (
    <>
      <section className="ai-insight-summary">
        <h4>Resumen</h4>

        <p>
          {result.summary
            || 'No se generó un resumen.'}
        </p>
      </section>

      <section className="ai-insight-result-section">
        <h4>Sugerencias de seguimiento</h4>

        {result.suggestions?.length ? (
          <div className="ai-insight-observation-list">
            {result.suggestions.map(
              (suggestion, index) => (
                <article
                  className="ai-insight-observation"
                  key={`${suggestion.title}-${index}`}
                >
                  <strong>
                    {suggestion.title}
                  </strong>

                  <p>
                    {suggestion.rationale}
                  </p>

                  {suggestion.related_data?.length > 0 && (
                    <div>
                      <span className="ai-insight-evidence-title">
                        Datos relacionados
                      </span>

                      <ul>
                        {suggestion.related_data.map(
                          (item, itemIndex) => (
                            <li
                              key={`${item}-${itemIndex}`}
                            >
                              {item}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </article>
              )
            )}
          </div>
        ) : (
          <p className="ai-insight-empty">
            No se generaron sugerencias.
          </p>
        )}
      </section>
    </>
  )
}


function RecommendationDetail({
  insight,
}) {
  const result = insight.result_json || {}

  return (
    <>
      <section className="ai-insight-summary">
        <h4>Resumen</h4>

        <p>
          {result.summary
            || 'No se generó un resumen.'}
        </p>
      </section>

      <section className="ai-insight-result-section">
        <h4>
          Recomendaciones de intervención
        </h4>

        {result.recommendations?.length ? (
          <div className="ai-insight-observation-list">
            {result.recommendations.map(
              (recommendation, index) => (
                <article
                  className="ai-insight-observation"
                  key={
                    `${recommendation.objective}-${index}`
                  }
                >
                  <strong>
                    {recommendation.objective}
                  </strong>

                  <p>
                    <b>Acción sugerida:</b>{' '}
                    {recommendation.action}
                  </p>

                  <p>
                    {recommendation.rationale}
                  </p>

                  {recommendation.related_data?.length > 0 && (
                    <div>
                      <span className="ai-insight-evidence-title">
                        Datos relacionados
                      </span>

                      <ul>
                        {recommendation.related_data.map(
                          (item, itemIndex) => (
                            <li
                              key={`${item}-${itemIndex}`}
                            >
                              {item}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                  {recommendation.cautions?.length > 0 && (
                    <div>
                      <span className="ai-insight-evidence-title">
                        Consideraciones profesionales
                      </span>

                      <ul>
                        {recommendation.cautions.map(
                          (item, itemIndex) => (
                            <li
                              key={`${item}-${itemIndex}`}
                            >
                              {item}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </article>
              )
            )}
          </div>
        ) : (
          <p className="ai-insight-empty">
            No se generaron recomendaciones.
          </p>
        )}
      </section>
    </>
  )
}


function ReviewControls({
  insight,
  context,
  reviewing,
  onReviewed,
  onError,
}) {
  const [professionalNotes, setProfessionalNotes] = (
    useState(
      insight.professional_notes || ''
    )
  )

  async function handleDecision(decision) {
    if (reviewing) {
      return
    }

    try {
      const updated = await reviewAIInsight(
        insight.id,
        {
          decision,
          professional_notes: professionalNotes,
        },
        context
      )

      onReviewed(updated)
    } catch (error) {
      onError(error)
    }
  }

  return (
    <section className="ai-insight-review">
      <div>
        <h4>Revisión profesional</h4>

        <p>
          Estado:{' '}
          <strong>
            {REVIEW_STATUS_LABELS[
              insight.review_status
            ] || insight.review_status}
          </strong>
        </p>
      </div>

      <label>
        Notas profesionales
        <textarea
          rows="4"
          value={professionalNotes}
          placeholder={
            'Registra observaciones sobre '
            + 'la utilidad o pertinencia del contenido.'
          }
          onChange={(event) => {
            setProfessionalNotes(
              event.target.value
            )
          }}
        />
      </label>

      <div className="ai-insight-review__actions">
        <button
          className="button button--primary"
          type="button"
          disabled={reviewing}
          onClick={() => {
            handleDecision('ACCEPTED')
          }}
        >
          Aceptar
        </button>

        <button
          className="button button--secondary"
          type="button"
          disabled={reviewing}
          onClick={() => {
            handleDecision('DISCARDED')
          }}
        >
          Descartar
        </button>

        {insight.kind === 'FOLLOWUP_SUGGESTION' && (
          <button
            className="button button--secondary"
            type="button"
            disabled={reviewing}
            onClick={() => {
              handleDecision('IGNORED')
            }}
          >
            Ignorar
          </button>
        )}
      </div>

      <p className="ai-insight-review__note">
        Esta decisión registra la revisión del
        profesional. No modifica automáticamente
        el expediente ni crea una intervención.
      </p>
    </section>
  )
}


function ReviewableDetail({
  insight,
  context,
  showContext,
  reviewing,
  onToggleContext,
  onReviewed,
  onError,
}) {
  const result = insight.result_json || {}

  return (
    <div className="ai-insight-detail">
      <div className="ai-insight-notice">
        <strong>
          Contenido generado por IA
        </strong>

        <p>
          {result.ai_notice}
        </p>
      </div>

      {insight.kind === 'FOLLOWUP_SUGGESTION' ? (
        <SuggestionDetail
          insight={insight}
        />
      ) : (
        <RecommendationDetail
          insight={insight}
        />
      )}

      <ReviewControls
        key={insight.id}
        insight={insight}
        context={context}
        reviewing={reviewing}
        onReviewed={onReviewed}
        onError={onError}
        />

      <ContextSection
        insight={insight}
        showContext={showContext}
        onToggleContext={onToggleContext}
      />
    </div>
  )
}


function InsightDetail({
  insight,
  context,
  showContext,
  reviewing,
  onToggleContext,
  onReviewed,
  onError,
}) {
  if (insight.kind === 'ANALYSIS') {
    return (
      <AnalysisDetail
        insight={insight}
        showContext={showContext}
        onToggleContext={onToggleContext}
      />
    )
  }

  return (
    <ReviewableDetail
      insight={insight}
      context={context}
      showContext={showContext}
      reviewing={reviewing}
      onToggleContext={onToggleContext}
      onReviewed={onReviewed}
      onError={onError}
    />
  )
}


export default function AIInsightPanel({
  studentId,
  context,
}) {
  const [activeMode, setActiveMode] = (
    useState('ANALYSIS')
  )

  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const [insights, setInsights] = useState([])
  const [selectedInsight, setSelectedInsight] = (
    useState(null)
  )

  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = (
    useState(false)
  )
  const [reviewing, setReviewing] = (
    useState(false)
  )
  const [openingId, setOpeningId] = useState(null)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showContext, setShowContext] = (
    useState(false)
  )

  useEffect(() => {
    let cancelled = false

    async function loadInsights() {
      setLoading(true)
      setError('')
      setSuccess('')
      setSelectedInsight(null)
      setShowContext(false)

      try {
        const response = await getAIInsights({
          context,
          studentId,
          kind: (
            activeMode === 'HISTORY'
              ? ''
              : activeMode
          ),
        })

        if (!cancelled) {
          setInsights(response.items || [])
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            getAIErrorMessage(loadError)
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadInsights()

    return () => {
      cancelled = true
    }
  }, [
    activeMode,
    context,
    studentId,
  ])

  async function refreshInsights() {
    const response = await getAIInsights({
      context,
      studentId,
      kind: (
        activeMode === 'HISTORY'
          ? ''
          : activeMode
      ),
    })

    setInsights(response.items || [])
  }

  async function handleGenerate(event) {
    event.preventDefault()

    if (
      generating
      || activeMode === 'HISTORY'
    ) {
      return
    }

    setGenerating(true)
    setError('')
    setSuccess('')
    setSelectedInsight(null)
    setShowContext(false)

    const payload = {
      student_id: studentId,
      kind: activeMode,
    }

    if (dateFrom) {
      payload.date_from = dateFrom
    }

    if (dateTo) {
      payload.date_to = dateTo
    }

    try {
      const insight = await createAIInsight(
        payload,
        context
      )

      setSelectedInsight(insight)

      setSuccess(
        'El contenido de apoyo fue generado '
        + 'correctamente.'
      )

      await refreshInsights()
    } catch (generateError) {
      setError(
        getAIErrorMessage(generateError)
      )
    } finally {
      setGenerating(false)
    }
  }

  async function handleOpen(insightId) {
    if (openingId) {
      return
    }

    setOpeningId(insightId)
    setError('')
    setSuccess('')
    setShowContext(false)

    try {
      const detail = await getAIInsight(
        insightId,
        context
      )

      setSelectedInsight(detail)
    } catch (openError) {
      setError(
        getAIErrorMessage(openError)
      )
    } finally {
      setOpeningId(null)
    }
  }

  async function handleReviewed(updated) {
    setReviewing(true)

    try {
      setSelectedInsight(updated)

      setSuccess(
        'La decisión profesional fue '
        + 'registrada correctamente.'
      )

      await refreshInsights()
    } finally {
      setReviewing(false)
    }
  }

  function handleReviewError(reviewError) {
    setReviewing(false)

    setError(
      getAIErrorMessage(reviewError)
    )
  }

  const activeConfig = (
    MODE_CONFIG[activeMode]
  )

  return (
    <div className="ai-insight-panel">
      <div className="ai-insight-introduction">
        <p>
          Utiliza información registrada y
          autorizada dentro de tu área profesional.
        </p>

        <p>
          Todo contenido generado funciona
          únicamente como apoyo profesional.
          No constituye diagnóstico ni ejecuta
          decisiones automáticamente.
        </p>
      </div>

      <div
        className="ai-insight-tabs"
        role="tablist"
        aria-label="Herramientas de inteligencia artificial"
      >
        {Object.entries(MODE_CONFIG).map(
          ([mode, config]) => (
            <button
              key={mode}
              type="button"
              role="tab"
              className={
                'ai-insight-tab '
                + (
                  activeMode === mode
                    ? 'ai-insight-tab--active'
                    : ''
                )
              }
              aria-selected={
                activeMode === mode
              }
              onClick={() => {
                setActiveMode(mode)
              }}
            >
              {config.label}
            </button>
          )
        )}
      </div>

      {activeMode !== 'HISTORY' && (
        <form
          className="ai-insight-form"
          onSubmit={handleGenerate}
        >
          <div>
            <h3>
              {activeConfig.title}
            </h3>

            <p>
              Selecciona opcionalmente un período
              para limitar la información utilizada.
            </p>
          </div>

          <div className="ai-insight-form__dates">
            <label>
              Desde
              <input
                type="date"
                value={dateFrom}
                onChange={(event) => {
                  setDateFrom(
                    event.target.value
                  )
                }}
              />
            </label>

            <label>
              Hasta
              <input
                type="date"
                value={dateTo}
                onChange={(event) => {
                  setDateTo(
                    event.target.value
                  )
                }}
              />
            </label>
          </div>

          <button
            className="button button--primary"
            type="submit"
            disabled={generating}
          >
            {generating
              ? activeConfig.loadingAction
              : activeConfig.action}
          </button>
        </form>
      )}

      {error && (
        <div
          className="form-message form-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      {success && (
        <div
          className="form-message form-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      {selectedInsight && (
        <InsightDetail
          insight={selectedInsight}
          context={context}
          showContext={showContext}
          reviewing={reviewing}
          onToggleContext={() => {
            setShowContext(
              (current) => !current
            )
          }}
          onReviewed={handleReviewed}
          onError={handleReviewError}
        />
      )}

      <section className="ai-insight-history">
        <div className="ai-insight-history__header">
          <div>
            <h3>
              {activeMode === 'HISTORY'
                ? 'Historial de asistencia IA'
                : 'Registros recientes'}
            </h3>

            <p>
              {activeMode === 'HISTORY'
                ? (
                  'Consulta análisis, sugerencias y '
                  + 'recomendaciones generadas '
                  + 'previamente.'
                )
                : (
                  'Consulta contenido generado '
                  + 'anteriormente en esta sección.'
                )}
            </p>
          </div>
        </div>

        {loading ? (
          <p>Cargando información...</p>
        ) : insights.length === 0 ? (
          <p className="ai-insight-empty">
            No existen registros para esta sección.
          </p>
        ) : (
          <div className="ai-insight-history__list">
            {insights.map((insight) => {
              const config = (
                MODE_CONFIG[insight.kind]
              )

              return (
                <article
                  className="ai-insight-history-card"
                  key={insight.id}
                >
                  <div>
                    <strong>
                      {config?.title
                        || insight.kind}
                    </strong>

                    <p>
                      Generado:{' '}
                      {formatDateTime(
                        insight.created_at
                      )}
                    </p>

                    <p>
                      Período:{' '}
                      {formatDate(
                        insight.date_from
                      )}
                      {' — '}
                      {formatDate(
                        insight.date_to
                      )}
                    </p>

                    {insight.kind !== 'ANALYSIS' && (
                      <p>
                        Estado:{' '}
                        <strong>
                          {
                            REVIEW_STATUS_LABELS[
                              insight.review_status
                            ]
                            || insight.review_status
                          }
                        </strong>
                      </p>
                    )}
                  </div>

                  <button
                    className="button button--secondary"
                    type="button"
                    disabled={
                      openingId === insight.id
                    }
                    onClick={() => {
                      handleOpen(insight.id)
                    }}
                  >
                    {openingId === insight.id
                    ? 'Abriendo...'
                    : (
                        insight.review_status === 'PENDING'
                        ? 'Abrir y revisar'
                        : 'Abrir'
                    )}
                  </button>
                </article>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
