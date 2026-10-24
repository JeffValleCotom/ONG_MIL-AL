import { useEffect, useState } from 'react'

import {
  createStudentAssignment,
  finishStudentAssignment,
  getEligibleProfessionals,
  getStudentAssignments,
} from '../services/studentService'


const PROFESSIONAL_ROLES = [
  {
    value: 'DOCENTE',
    label: 'Docente',
  },
  {
    value: 'PSICOLOGO',
    label: 'Psicólogo',
  },
  {
    value: 'TERAPEUTA',
    label: 'Terapeuta',
  },
]


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
      dateStyle: 'short',
      timeStyle: 'short',
    }
  ).format(date)
}


function getProfessionalName(professional) {
  const fullName = [
    professional.first_name,
    professional.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return fullName || professional.username
}


function getAssignmentErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible completar la operación.'
    )
  }

  const fieldOrder = [
    'student_id',
    'professional_id',
    'professional_role',
    'role',
    'non_field_errors',
    'detail',
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


function StudentAssignmentManager({
  student,
}) {
  const [assignments, setAssignments] = useState([])
  const [professionals, setProfessionals] = useState([])

  const [selectedRole, setSelectedRole] =
    useState('DOCENTE')

  const [selectedProfessionalId, setSelectedProfessionalId] =
    useState('')

  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingProfessionals, setIsLoadingProfessionals] =
    useState(false)
  const [isSubmitting, setIsSubmitting] =
    useState(false)
  const [finishingId, setFinishingId] =
    useState(null)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function loadAssignments() {
    const data = await getStudentAssignments({
      studentId: student.id,
    })

    setAssignments(data)
  }

  useEffect(() => {
    let isMounted = true

    async function loadInitialAssignments() {
      setIsLoading(true)
      setError('')

      try {
        const data = await getStudentAssignments({
          studentId: student.id,
        })

        if (isMounted) {
          setAssignments(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            getAssignmentErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadInitialAssignments()

    return () => {
      isMounted = false
    }
  }, [student.id])

  useEffect(() => {
    let isMounted = true

    async function loadProfessionals() {
      setIsLoadingProfessionals(true)
      setSelectedProfessionalId('')
      setError('')

      try {
        const data = await getEligibleProfessionals(
          selectedRole
        )

        if (isMounted) {
          setProfessionals(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setProfessionals([])
          setError(
            getAssignmentErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoadingProfessionals(false)
        }
      }
    }

    loadProfessionals()

    return () => {
      isMounted = false
    }
  }, [selectedRole])

  async function handleSubmit(event) {
    event.preventDefault()

    if (
      !selectedProfessionalId
      || isSubmitting
      || !student.is_active
    ) {
      return
    }

    setIsSubmitting(true)
    setError('')
    setSuccess('')

    try {
      await createStudentAssignment({
        studentId: student.id,
        professionalId: Number(
          selectedProfessionalId
        ),
        professionalRole: selectedRole,
      })

      await loadAssignments()

      setSelectedProfessionalId('')
      setSuccess(
        'Profesional asignado correctamente.'
      )
    } catch (submitError) {
      setError(
        getAssignmentErrorMessage(submitError)
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleFinish(assignment) {
    if (finishingId !== null) {
      return
    }

    const confirmed = window.confirm(
      '¿Deseas finalizar esta asignación? '
      + 'El registro se conservará en el historial.'
    )

    if (!confirmed) {
      return
    }

    setFinishingId(assignment.id)
    setError('')
    setSuccess('')

    try {
      const response = await finishStudentAssignment(
        assignment.id
      )

      await loadAssignments()

      setSuccess(
        response.detail
        || 'Asignación finalizada correctamente.'
      )
    } catch (finishError) {
      setError(
        getAssignmentErrorMessage(finishError)
      )
    } finally {
      setFinishingId(null)
    }
  }

  return (
    <div className="student-assignments">
      <section className="student-assignments__summary">
        <strong>
          {student.institutional_code}
        </strong>

        <span>
          {student.first_name}
          {' '}
          {student.last_name}
        </span>
      </section>

      {!student.is_active && (
        <div
          className="students-message students-message--error"
          role="alert"
        >
          El estudiante está inactivo. Puedes consultar
          su historial, pero no crear nuevas asignaciones.
        </div>
      )}

      {success && (
        <div
          className="students-message students-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      {error && (
        <div
          className="students-message students-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      <form
        className="student-assignment-form"
        onSubmit={handleSubmit}
      >
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="assignment-role">
              Rol profesional
            </label>

            <select
              id="assignment-role"
              value={selectedRole}
              onChange={(event) => {
                setSelectedRole(event.target.value)
              }}
              disabled={
                isSubmitting
                || !student.is_active
              }
            >
              {PROFESSIONAL_ROLES.map((role) => (
                <option
                  key={role.value}
                  value={role.value}
                >
                  {role.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="assignment-professional">
              Profesional
            </label>

            <select
              id="assignment-professional"
              value={selectedProfessionalId}
              onChange={(event) => {
                setSelectedProfessionalId(
                  event.target.value
                )
              }}
              disabled={
                isSubmitting
                || isLoadingProfessionals
                || !student.is_active
              }
            >
              <option value="">
                {isLoadingProfessionals
                  ? 'Cargando profesionales...'
                  : 'Selecciona un profesional'}
              </option>

              {professionals.map((professional) => (
                <option
                  key={professional.id}
                  value={professional.id}
                >
                  {getProfessionalName(professional)}
                  {' — '}
                  {professional.username}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="button button--primary"
            type="submit"
            disabled={
              isSubmitting
              || !selectedProfessionalId
              || !student.is_active
            }
          >
            {isSubmitting
              ? 'Asignando...'
              : 'Asignar profesional'}
          </button>
        </div>
      </form>

      <section
        className="student-assignment-history"
        aria-labelledby="assignment-history-title"
      >
        <h3 id="assignment-history-title">
          Historial de asignaciones
        </h3>

        {isLoading && (
          <div className="students-empty">
            Cargando asignaciones...
          </div>
        )}

        {!isLoading && assignments.length === 0 && (
          <div className="students-empty">
            No existen asignaciones para este estudiante.
          </div>
        )}

        {!isLoading && assignments.length > 0 && (
          <div className="table-container">
            <table className="students-table">
              <thead>
                <tr>
                  <th scope="col">
                    Rol
                  </th>

                  <th scope="col">
                    Profesional
                  </th>

                  <th scope="col">
                    Asignado
                  </th>

                  <th scope="col">
                    Estado
                  </th>

                  <th scope="col">
                    Acción
                  </th>
                </tr>
              </thead>

              <tbody>
                {assignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td>
                      {assignment.professional_role}
                    </td>

                    <td>
                      {getProfessionalName(
                        assignment.professional
                      )}
                    </td>

                    <td>
                      {formatDateTime(
                        assignment.assigned_at
                      )}
                    </td>

                    <td>
                      <span
                        className={
                          assignment.is_active
                            ? 'status status--active'
                            : 'status status--inactive'
                        }
                      >
                        {assignment.is_active
                          ? 'Activa'
                          : 'Finalizada'}
                      </span>
                    </td>

                    <td>
                      {assignment.is_active
                        ? (
                          <button
                            className="button button--danger"
                            type="button"
                            disabled={
                              finishingId !== null
                            }
                            onClick={() => {
                              handleFinish(assignment)
                            }}
                          >
                            {finishingId === assignment.id
                              ? 'Finalizando...'
                              : 'Finalizar'}
                          </button>
                        )
                        : (
                          <span>
                            {formatDateTime(
                              assignment.unassigned_at
                            )}
                          </span>
                        )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}


export default StudentAssignmentManager
