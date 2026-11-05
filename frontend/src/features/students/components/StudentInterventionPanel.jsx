import { useState } from 'react'

import {
  createStudentInterventionPlan,
  updateStudentInterventionPlan,
  createStudentInterventionFollowUp,
} from '../services/studentService'
import AppModal
  from '../../../components/ui/AppModal'

import './StudentInterventionPanel.css'


const STATUS_LABELS = {
  PLANNED: 'Planificada',
  IN_PROGRESS: 'En progreso',
  COMPLETED: 'Completada',
  CANCELLED: 'Cancelada',
}


function todayValue() {
  const now = new Date()
  const offset = now.getTimezoneOffset()

  return new Date(
    now.getTime() - offset * 60 * 1000
  )
    .toISOString()
    .slice(0, 10)
}


function getErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return 'No fue posible completar la operación.'
  }

  const fields = [
    'objectives',
    'observations',
    'intervention_date',
    'estimated_start_date',
    'estimated_end_date',
    'responsible_id',
    'responsible_role',
    'status',
    'student',
    'detail',
  ]

  for (const field of fields) {
    const value = data[field]

    if (Array.isArray(value) && value.length) {
      return value[0]
    }

    if (typeof value === 'string') {
      return value
    }
  }

  return 'No fue posible completar la operación.'
}


function formatDate(value) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  return `${day}/${month}/${year}`
}


function professionalName(professional) {
  if (!professional) {
    return 'Sin responsable'
  }

  const fullName = [
    professional.first_name,
    professional.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return fullName || professional.username
}


function StudentInterventionPanel({
  studentId,
  context,
  performed = [],
  planned = [],
  responsibleOptions = [],
  canManage = false,
  onChanged,
}) {
  const [
    activeForm,
    setActiveForm,
  ] = useState('')

  const [
    editingPlan,
    setEditingPlan,
  ] = useState(null)

  const [
    isSaving,
    setIsSaving,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState('')

  const [
    success,
    setSuccess,
  ] = useState('')

  const [
    planForm,
    setPlanForm,
  ] = useState({
    objectives: '',
    estimated_start_date: todayValue(),
    estimated_end_date: '',
    responsible_key: '',
  })

  const [
    followUpPlan,
    setFollowUpPlan,
  ] = useState(null)

  const [
    historyPlan,
    setHistoryPlan,
  ] = useState(null)

  const [
    detailIntervention,
    setDetailIntervention,
  ] = useState(null)

  const [
    followUpForm,
    setFollowUpForm,
  ] = useState({
    followup_date: todayValue(),
    progress: '',
    results: '',
    observations: '',
    status: 'IN_PROGRESS',
  })


  function openPlanForm(plan = null) {
    setError('')
    setSuccess('')
    setEditingPlan(plan)

    setPlanForm({
      objectives:
        plan?.objectives ?? '',
      estimated_start_date:
        plan?.estimated_start_date
        ?? todayValue(),
      estimated_end_date:
        plan?.estimated_end_date ?? '',
      responsible_key: plan
        ? `${plan.responsible?.id}|${plan.responsible_role}`
        : '',
    })

    setActiveForm('plan')
  }


  function cancelForm() {
    if (isSaving) {
      return
    }

    setActiveForm('')
    setEditingPlan(null)
    setError('')
    setFollowUpPlan(null)
  }

  function openFollowUpForm(plan) {
    setError('')
    setSuccess('')
    setEditingPlan(null)
    setFollowUpPlan(plan)

    setFollowUpForm({
      followup_date: todayValue(),
      progress: '',
      results: '',
      observations: '',
      status: (
        plan.status === 'PLANNED'
          ? 'IN_PROGRESS'
          : plan.status
      ),
    })

    setActiveForm('followup')
  }

  async function refreshAfterSave(message) {
    setActiveForm('')
    setEditingPlan(null)
    setSuccess(message)
    setFollowUpPlan(null)

    if (onChanged) {
      await onChanged()
    }
  }

  async function submitPlan(event) {
    event.preventDefault()

    if (isSaving) {
      return
    }

    const [
      responsibleId,
      responsibleRole,
    ] = planForm.responsible_key.split('|')

    if (!responsibleId || !responsibleRole) {
      setError(
        'Selecciona un responsable para la planificación.'
      )
      return
    }

    const payload = {
      objectives: planForm.objectives,
      estimated_start_date:
        planForm.estimated_start_date,
      estimated_end_date:
        planForm.estimated_end_date || null,
      responsible_id: Number(responsibleId),
      responsible_role: responsibleRole,
    }

    setIsSaving(true)
    setError('')
    setSuccess('')

    try {
      if (editingPlan) {
        await updateStudentInterventionPlan(
          studentId,
          editingPlan.id,
          payload,
          context
        )

        await refreshAfterSave(
          'Planificación actualizada correctamente.'
        )
      } else {
        await createStudentInterventionPlan(
          studentId,
          payload,
          context
        )

        await refreshAfterSave(
          'Planificación creada correctamente.'
        )
      }
    } catch (saveError) {
      setError(
        getErrorMessage(saveError)
      )
    } finally {
      setIsSaving(false)
    }
  }

  async function submitFollowUp(event) {
    event.preventDefault()

    if (
      isSaving
      || !followUpPlan
    ) {
      return
    }

    setIsSaving(true)
    setError('')
    setSuccess('')

    try {
      await createStudentInterventionFollowUp(
        studentId,
        followUpPlan.id,
        followUpForm,
        context
      )

      await refreshAfterSave(
        'Seguimiento registrado correctamente.'
      )
    } catch (saveError) {
      setError(
        getErrorMessage(saveError)
      )
    } finally {
      setIsSaving(false)
    }
  }

  const activePlans = planned.filter(
    (plan) => (
      plan.status === 'PLANNED'
      || plan.status === 'IN_PROGRESS'
    ),
  )

  const completedPlans = planned.filter(
    (plan) => plan.status === 'COMPLETED',
  )

  return (
    <div className="student-interventions">
      {success && (
        <div
          className="form-message form-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      {error && !activeForm && (
        <div
          className="form-message form-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      {canManage && (
        <div className="student-interventions__actions">
          <button
            className="button button--primary"
            type="button"
            onClick={() => openPlanForm()}
          >
            + Nueva planificación
          </button>
        </div>
      )}

      {activeForm === 'plan' && (
        <AppModal
          isOpen
          title={
            editingPlan
              ? 'Editar planificación'
              : 'Nueva planificación'
          }
          subtitle={
            editingPlan
              ? (
                  'Actualiza los objetivos, fechas y '
                  + 'responsable de la planificación.'
                )
              : (
                  'Define los objetivos, período y '
                  + 'responsable de la intervención.'
                )
          }
          onClose={cancelForm}
          closeDisabled={isSaving}
          size="md"
        >
          <form
            className="student-interventions__form"
            onSubmit={submitPlan}
          >

          {error && (
            <div
              className="form-message form-message--error"
              role="alert"
            >
              {error}
            </div>
          )}

          <label>
            Objetivos
            <textarea
              required
              value={planForm.objectives}
              onChange={(event) => {
                setPlanForm({
                  ...planForm,
                  objectives: event.target.value,
                })
              }}
            />
          </label>

          <div className="student-interventions__grid">
            <label>
              Fecha inicial estimada
              <input
                type="date"
                required
                value={
                  planForm.estimated_start_date
                }
                onChange={(event) => {
                  setPlanForm({
                    ...planForm,
                    estimated_start_date:
                      event.target.value,
                  })
                }}
              />
            </label>

            <label>
              Fecha final estimada
              <input
                type="date"
                value={
                  planForm.estimated_end_date
                }
                onChange={(event) => {
                  setPlanForm({
                    ...planForm,
                    estimated_end_date:
                      event.target.value,
                  })
                }}
              />
            </label>
          </div>

          <label>
            Responsable
            <select
              required
              value={planForm.responsible_key}
              onChange={(event) => {
                setPlanForm({
                  ...planForm,
                  responsible_key:
                    event.target.value,
                })
              }}
            >
              <option value="">
                Selecciona un responsable
              </option>

              {responsibleOptions.map((option) => (
                <option
                  key={
                    `${option.professional.id}-`
                    + option.professional_role
                  }
                  value={
                    `${option.professional.id}|`
                    + option.professional_role
                  }
                >
                  {professionalName(
                    option.professional
                  )}
                  {' — '}
                  {option.professional_role}
                </option>
              ))}
            </select>
          </label>

          <div className="student-interventions__actions">
            <button
              className="button button--primary"
              type="submit"
              disabled={isSaving}
            >
              {isSaving
                ? 'Guardando...'
                : 'Guardar planificación'}
            </button>

            <button
              className="button button--secondary"
              type="button"
              onClick={cancelForm}
              disabled={isSaving}
            >
              Cancelar
            </button>
          </div>
        </form>
        </AppModal>
      )}

      {activeForm === 'followup' && followUpPlan && (
        <AppModal
          isOpen
          title="Registrar avance"
          subtitle={
            'Actualiza el progreso y estado de la '
            + 'planificación seleccionada.'
          }
          onClose={cancelForm}
          closeDisabled={isSaving}
          size="md"
        >
          <form
            className="student-interventions__form"
            onSubmit={submitFollowUp}
          >
            <div className="student-interventions__modal-context">
              <span>
                Objetivo de la intervención
              </span>

              <strong>
                {followUpPlan.objectives}
              </strong>
            </div>

          {error && (
            <div
              className="form-message form-message--error"
              role="alert"
            >
              {error}
            </div>
          )}

          <label>
            Fecha del seguimiento
            <input
              type="date"
              required
              max={todayValue()}
              value={followUpForm.followup_date}
              onChange={(event) => {
                setFollowUpForm({
                  ...followUpForm,
                  followup_date:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Avances
            <textarea
              required
              value={followUpForm.progress}
              onChange={(event) => {
                setFollowUpForm({
                  ...followUpForm,
                  progress:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Resultados
            <textarea
              required
              value={followUpForm.results}
              onChange={(event) => {
                setFollowUpForm({
                  ...followUpForm,
                  results:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Observaciones
            <textarea
              required
              value={followUpForm.observations}
              onChange={(event) => {
                setFollowUpForm({
                  ...followUpForm,
                  observations:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Estado resultante
            <select
              value={followUpForm.status}
              onChange={(event) => {
                setFollowUpForm({
                  ...followUpForm,
                  status:
                    event.target.value,
                })
              }}
            >
              {followUpPlan.status === 'PLANNED' && (
                <>
                  <option value="PLANNED">
                    Planificada
                  </option>
                  <option value="IN_PROGRESS">
                    En progreso
                  </option>
                  <option value="CANCELLED">
                    Cancelada
                  </option>
                </>
              )}

              {followUpPlan.status === 'IN_PROGRESS' && (
                <>
                  <option value="IN_PROGRESS">
                    En progreso
                  </option>
                  <option value="COMPLETED">
                    Completada
                  </option>
                  <option value="CANCELLED">
                    Cancelada
                  </option>
                </>
              )}
            </select>
          </label>

          <div className="student-interventions__actions">
            <button
              className="button button--primary"
              type="submit"
              disabled={isSaving}
            >
              {isSaving
                ? 'Guardando...'
                : 'Registrar seguimiento'}
            </button>

            <button
              className="button button--secondary"
              type="button"
              onClick={cancelForm}
              disabled={isSaving}
            >
              Cancelar
            </button>
          </div>
        </form>
        </AppModal>
      )}

      <section className="student-interventions__section">
        <h3>Planificaciones activas</h3>

        {activePlans.length === 0 ? (
          <p className="student-interventions__empty">
            No hay intervenciones planificadas.
          </p>
        ) : (
          <div className="student-interventions__list">
            {activePlans.map((plan) => (
              <article
                className={
                  'student-interventions__item '
                  + 'student-interventions__item--planned'
                }
                key={plan.id}
              >
                <div className="student-interventions__item-main">
                  <div className="student-interventions__item-topline">
                    <span className="student-interventions__status">
                      {STATUS_LABELS[plan.status]
                        ?? plan.status}
                    </span>

                    <span className="student-interventions__dates">
                      {formatDate(
                        plan.estimated_start_date
                      )}

                      {plan.estimated_end_date
                        ? (
                            ` — ${formatDate(
                              plan.estimated_end_date,
                            )}`
                          )
                        : ''}
                    </span>
                  </div>

                  <p className="student-interventions__objective">
                    {plan.objectives}
                  </p>

                  <p className="student-interventions__responsible">
                    Responsable:{' '}
                    <strong>
                      {professionalName(
                        plan.responsible
                      )}
                    </strong>
                  </p>
                </div>

                <div className="student-interventions__item-actions">
                  {canManage && (
                    <button
                      className="button button--secondary"
                      type="button"
                      onClick={() => openPlanForm(plan)}
                    >
                      Editar
                    </button>
                  )}

                  {canManage
                    && (
                      plan.status === 'PLANNED'
                      || plan.status === 'IN_PROGRESS'
                    ) && (
                    <button
                      className="button button--primary"
                      type="button"
                      onClick={() => openFollowUpForm(plan)}
                    >
                      Registrar avance
                    </button>
                  )}

                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => {
                      setHistoryPlan(plan)
                    }}
                  >
                    Ver historial ({(plan.followups ?? []).length})
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <AppModal
        isOpen={Boolean(historyPlan)}
        title="Historial de seguimiento"
        subtitle={
          historyPlan
            ? (
                'Consulta los avances registrados para '
                + 'esta planificación.'
              )
            : ''
        }
        onClose={() => {
          setHistoryPlan(null)
        }}
        size="lg"
      >
        {historyPlan && (
          <div className="student-interventions__history">
            <div className="student-interventions__history-context">
              <span>
                Objetivo de la intervención
              </span>

              <strong>
                {historyPlan.objectives}
              </strong>

              <small>
                Responsable:{' '}
                {professionalName(
                  historyPlan.responsible
                )}
              </small>
            </div>

            {(historyPlan.followups ?? []).length === 0 ? (
              <div className="student-interventions__history-empty">
                <span aria-hidden="true">
                  ○
                </span>

                <strong>
                  Sin seguimientos registrados
                </strong>

                <p>
                  Todavía no se han registrado avances
                  para esta planificación.
                </p>
              </div>
            ) : (
              <div className="student-interventions__followup-list">
                {historyPlan.followups.map((followUp) => (
                  <article
                    key={followUp.id}
                    className="student-interventions__followup"
                  >
                    <div className="student-interventions__followup-header">
                      <strong>
                        {formatDate(
                          followUp.followup_date,
                        )}
                      </strong>

                      <span className="student-interventions__status">
                        {STATUS_LABELS[followUp.status]
                          ?? followUp.status}
                      </span>
                    </div>

                    <dl className="student-interventions__followup-details">
                      <div>
                        <dt>Avances</dt>
                        <dd>
                          {followUp.progress}
                        </dd>
                      </div>

                      <div>
                        <dt>Resultados</dt>
                        <dd>
                          {followUp.results}
                        </dd>
                      </div>

                      <div>
                        <dt>Observaciones</dt>
                        <dd>
                          {followUp.observations}
                        </dd>
                      </div>
                    </dl>

                    <small>
                      Registrado por:{' '}
                      {professionalName(
                        followUp.created_by
                      )}
                    </small>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}
      </AppModal>

      <section className="student-interventions__section">
        <h3>Intervenciones realizadas</h3>

        {completedPlans.length === 0
          && performed.length === 0 ? (
          <p className="student-interventions__empty">
            No hay intervenciones completadas.
          </p>
        ) : (
          <div className="student-interventions__list">
            {completedPlans.map((plan) => (
              <article
                className={
                  'student-interventions__item '
                  + 'student-interventions__item--completed'
                }
                key={`completed-${plan.id}`}
              >
                <div className="student-interventions__item-main">
                  <div className="student-interventions__item-topline">
                    <span className="student-interventions__status">
                      Completada
                    </span>

                    <span className="student-interventions__dates">
                      {formatDate(
                        plan.estimated_start_date,
                      )}

                      {plan.estimated_end_date
                        ? (
                            ` — ${formatDate(
                              plan.estimated_end_date,
                            )}`
                          )
                        : ''}
                    </span>
                  </div>

                  <p className="student-interventions__objective">
                    {plan.objectives}
                  </p>

                  <p className="student-interventions__responsible">
                    Responsable:{' '}
                    <strong>
                      {professionalName(
                        plan.responsible,
                      )}
                    </strong>
                  </p>
                </div>

                <div className="student-interventions__item-actions">
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => {
                      setHistoryPlan(plan)
                    }}
                  >
                    Ver historial (
                    {(plan.followups ?? []).length}
                    )
                  </button>
                </div>
              </article>
            ))}

            {performed.map((intervention) => (
              <article
                className={
                  'student-interventions__item '
                  + 'student-interventions__item--legacy'
                }
                key={`performed-${intervention.id}`}
              >
                <div className="student-interventions__item-main">
                  <div className="student-interventions__item-topline">
                    <span className="student-interventions__status">
                      Registro directo
                    </span>

                    <span className="student-interventions__dates">
                      {formatDate(
                        intervention.intervention_date,
                      )}
                    </span>
                  </div>

                  <p className="student-interventions__objective">
                    {intervention.objectives}
                  </p>

                  <p className="student-interventions__responsible">
                    Intervención registrada previamente
                  </p>
                </div>

                <div className="student-interventions__item-actions">
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => {
                      setDetailIntervention(
                        intervention,
                      )
                    }}
                  >
                    Ver detalle
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
      <AppModal
        isOpen={Boolean(detailIntervention)}
        title="Detalle de la intervención"
        subtitle={
          'Consulta la información histórica '
          + 'de esta intervención.'
        }
        onClose={() => {
          setDetailIntervention(null)
        }}
        size="md"
      >
        {detailIntervention && (
          <div className="student-interventions__history">
            <div className="student-interventions__history-context">
              <span>
                Fecha de intervención
              </span>

              <strong>
                {formatDate(
                  detailIntervention.intervention_date,
                )}
              </strong>
            </div>

            <dl className="student-interventions__followup-details">
              <div>
                <dt>Objetivos</dt>
                <dd>
                  {detailIntervention.objectives}
                </dd>
              </div>

              <div>
                <dt>Observaciones</dt>
                <dd>
                  {detailIntervention.observations || '—'}
                </dd>
              </div>
            </dl>
          </div>
        )}
      </AppModal>
    </div>
  )
}


export default StudentInterventionPanel
