import { useState } from 'react'

import {
  createStudentIntervention,
  updateStudentIntervention,
  createStudentInterventionPlan,
  updateStudentInterventionPlan,
} from '../services/studentService'

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
    editingPerformed,
    setEditingPerformed,
  ] = useState(null)

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
    performedForm,
    setPerformedForm,
  ] = useState({
    intervention_date: todayValue(),
    objectives: '',
    observations: '',
  })

  const [
    planForm,
    setPlanForm,
  ] = useState({
    objectives: '',
    estimated_start_date: todayValue(),
    estimated_end_date: '',
    responsible_key: '',
    status: 'PLANNED',
  })


  function openPerformedForm(intervention = null) {
    setError('')
    setSuccess('')
    setEditingPlan(null)
    setEditingPerformed(intervention)

    setPerformedForm({
      intervention_date:
        intervention?.intervention_date
        ?? todayValue(),
      objectives:
        intervention?.objectives ?? '',
      observations:
        intervention?.observations ?? '',
    })

    setActiveForm('performed')
  }


  function openPlanForm(plan = null) {
    setError('')
    setSuccess('')
    setEditingPerformed(null)
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
      status:
        plan?.status ?? 'PLANNED',
    })

    setActiveForm('plan')
  }


  function cancelForm() {
    if (isSaving) {
      return
    }

    setActiveForm('')
    setEditingPerformed(null)
    setEditingPlan(null)
    setError('')
  }


  async function refreshAfterSave(message) {
    setActiveForm('')
    setEditingPerformed(null)
    setEditingPlan(null)
    setSuccess(message)

    if (onChanged) {
      await onChanged()
    }
  }


  async function submitPerformed(event) {
    event.preventDefault()

    if (isSaving) {
      return
    }

    setIsSaving(true)
    setError('')
    setSuccess('')

    try {
      if (editingPerformed) {
        await updateStudentIntervention(
          studentId,
          editingPerformed.id,
          performedForm,
          context
        )

        await refreshAfterSave(
          'Intervención actualizada correctamente.'
        )
      } else {
        await createStudentIntervention(
          studentId,
          performedForm,
          context
        )

        await refreshAfterSave(
          'Intervención registrada correctamente.'
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
      status: planForm.status,
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

      {canManage && !activeForm && (
        <div className="student-interventions__actions">
          <button
            className="button button--primary"
            type="button"
            onClick={() => openPlanForm()}
          >
            Nueva planificación
          </button>

          <button
            className="button button--secondary"
            type="button"
            onClick={() => openPerformedForm()}
          >
            Registrar intervención
          </button>
        </div>
      )}

      {activeForm === 'plan' && (
        <form
          className="student-interventions__form"
          onSubmit={submitPlan}
        >
          <h3>
            {editingPlan
              ? 'Editar planificación'
              : 'Nueva planificación'}
          </h3>

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

          {editingPlan && (
            <label>
              Estado
              <select
                value={planForm.status}
                onChange={(event) => {
                  setPlanForm({
                    ...planForm,
                    status: event.target.value,
                  })
                }}
              >
                <option value="PLANNED">
                  Planificada
                </option>
                <option value="IN_PROGRESS">
                  En progreso
                </option>
                <option value="COMPLETED">
                  Completada
                </option>
                <option value="CANCELLED">
                  Cancelada
                </option>
              </select>
            </label>
          )}

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
      )}

      {activeForm === 'performed' && (
        <form
          className="student-interventions__form"
          onSubmit={submitPerformed}
        >
          <h3>
            {editingPerformed
              ? 'Editar intervención'
              : 'Registrar intervención'}
          </h3>

          {error && (
            <div
              className="form-message form-message--error"
              role="alert"
            >
              {error}
            </div>
          )}

          <label>
            Fecha
            <input
              type="date"
              required
              value={
                performedForm.intervention_date
              }
              onChange={(event) => {
                setPerformedForm({
                  ...performedForm,
                  intervention_date:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Objetivos
            <textarea
              required
              value={performedForm.objectives}
              onChange={(event) => {
                setPerformedForm({
                  ...performedForm,
                  objectives:
                    event.target.value,
                })
              }}
            />
          </label>

          <label>
            Observaciones
            <textarea
              required
              value={performedForm.observations}
              onChange={(event) => {
                setPerformedForm({
                  ...performedForm,
                  observations:
                    event.target.value,
                })
              }}
            />
          </label>

          <div className="student-interventions__actions">
            <button
              className="button button--primary"
              type="submit"
              disabled={isSaving}
            >
              {isSaving
                ? 'Guardando...'
                : 'Guardar intervención'}
            </button>

            <button
              className="button button--secondary"
              type="button"
              disabled={isSaving}
              onClick={cancelForm}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      <section className="student-interventions__section">
        <h3>Intervenciones planificadas</h3>

        {planned.length === 0 ? (
          <p className="student-interventions__empty">
            No hay intervenciones planificadas.
          </p>
        ) : (
          <div className="student-interventions__list">
            {planned.map((plan) => (
              <article
                className="student-interventions__item"
                key={plan.id}
              >
                <div>
                  <strong>
                    {STATUS_LABELS[plan.status]
                      ?? plan.status}
                  </strong>

                  <p>{plan.objectives}</p>

                  <small>
                    {formatDate(
                      plan.estimated_start_date
                    )}
                    {plan.estimated_end_date
                      ? ` — ${formatDate(
                        plan.estimated_end_date
                      )}`
                      : ''}
                  </small>

                  <small>
                    Responsable:{' '}
                    {professionalName(
                      plan.responsible
                    )}
                  </small>
                </div>

                {canManage && (
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => openPlanForm(plan)}
                  >
                    Editar
                  </button>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="student-interventions__section">
        <h3>Intervenciones realizadas</h3>

        {performed.length === 0 ? (
          <p className="student-interventions__empty">
            No hay intervenciones registradas.
          </p>
        ) : (
          <div className="student-interventions__list">
            {performed.map((intervention) => (
              <article
                className="student-interventions__item"
                key={intervention.id}
              >
                <div>
                  <strong>
                    {formatDate(
                      intervention.intervention_date
                    )}
                  </strong>

                  <p>
                    <b>Objetivos:</b>{' '}
                    {intervention.objectives}
                  </p>

                  <p>
                    <b>Observaciones:</b>{' '}
                    {intervention.observations}
                  </p>
                </div>

                {canManage && (
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => {
                      openPerformedForm(
                        intervention
                      )
                    }}
                  >
                    Editar
                  </button>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}


export default StudentInterventionPanel
