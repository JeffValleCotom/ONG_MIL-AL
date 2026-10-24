import { useEffect, useState } from 'react'

import ConfirmDialog from '../../../components/ConfirmDialog'
import Modal from '../../../components/Modal'
import '../../../components/Modal.css'
import StudentAssignmentManager
  from '../components/StudentAssignmentManager'
import StudentEditForm
  from '../components/StudentEditForm'
import StudentRegistrationForm
  from '../components/StudentRegistrationForm'
import StudentTable
  from '../components/StudentTable'
import {
  activateStudent,
  createStudent,
  deactivateStudent,
  getStudents,
  updateStudent,
} from '../services/studentService'
import './StudentManagementPage.css'

function getStudentErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message ||
      'No fue posible completar la operación.'
    )
  }

  const fieldOrder = [
    'institutional_code',
    'first_name',
    'last_name',
    'date_of_birth',
    'admission_date',
    'is_active',
    'status',
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
    error?.message ||
    'No fue posible completar la operación.'
  )
}


function StudentManagementPage({
  onLogout,
  onChangeSpace,
  canManageStudents = false,
  studentContext = '',
  pageEyebrow = 'Gestión de estudiantes',
  pageTitle = 'Estudiantes',
  pageDescription = '',
}) {
  const [students, setStudents] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [isUpdating, setIsUpdating] =
    useState(false)

  const [isChangingStatus, setIsChangingStatus] =
    useState(false)

  const [listError, setListError] = useState('')
  const [registrationError, setRegistrationError] =
    useState('')
  const [editError, setEditError] = useState('')
  const [actionError, setActionError] = useState('')
  const [success, setSuccess] = useState('')

  const [editingStudent, setEditingStudent] =
    useState(null)

  const [statusStudent, setStatusStudent] =
    useState(null)

  const [formVersion, setFormVersion] =
    useState(0)

  const [searchInput, setSearchInput] =
    useState('')

  const [statusInput, setStatusInput] =
    useState('')

  const [filters, setFilters] = useState({
    search: '',
    status: '',
  })
  const [assignmentStudent, setAssignmentStudent] =
    useState(null)

  useEffect(() => {
    let isMounted = true

    async function loadStudents() {
      setIsLoading(true)
      setListError('')

      try {
        const data = await getStudents({
          ...filters,
          context: studentContext,
        })

        if (isMounted) {
          setStudents(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setListError(
            getStudentErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadStudents()

    return () => {
      isMounted = false
    }
  }, [filters, studentContext])

  async function refreshStudents() {
    const data = await getStudents({
      ...filters,
      context: studentContext,
    })

    setStudents(data)
  }

  async function handleStudentSubmit(studentData) {
    setIsSubmitting(true)
    setRegistrationError('')
    setActionError('')
    setSuccess('')

    try {
      const student = await createStudent(
        studentData
      )

      await refreshStudents()

      setSuccess(
        `Estudiante ${student.institutional_code} `
        + 'registrado correctamente.'
      )

      setFormVersion((current) => current + 1)
    } catch (registrationErrorResponse) {
      setRegistrationError(
        getStudentErrorMessage(
          registrationErrorResponse
        )
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleEdit(student) {
    setEditingStudent(student)
    setEditError('')
    setActionError('')
    setSuccess('')
  }

  function handleEditCancel() {
    if (isUpdating) {
      return
    }

    setEditingStudent(null)
    setEditError('')
  }

  function handleManageAssignments(student) {
    setAssignmentStudent(student)
    setActionError('')
    setSuccess('')
  }


  function handleAssignmentsClose() {
    setAssignmentStudent(null)
  }

  async function handleStudentUpdate(studentData) {
    if (!editingStudent || isUpdating) {
      return
    }

    setIsUpdating(true)
    setEditError('')
    setActionError('')
    setSuccess('')

    try {
      const updatedStudent = await updateStudent(
        editingStudent.id,
        studentData
      )

      await refreshStudents()

      setEditingStudent(null)

      setSuccess(
        `Estudiante `
        + `${updatedStudent.institutional_code} `
        + 'actualizado correctamente.'
      )
    } catch (updateError) {
      setEditError(
        getStudentErrorMessage(updateError)
      )
    } finally {
      setIsUpdating(false)
    }
  }

  function handleToggleStatus(student) {
    setStatusStudent(student)
    setActionError('')
    setSuccess('')
  }

  function handleStatusCancel() {
    if (isChangingStatus) {
      return
    }

    setStatusStudent(null)
  }

  async function handleStatusConfirm() {
    if (!statusStudent || isChangingStatus) {
      return
    }

    const student = statusStudent
    const shouldDeactivate = student.is_active

    setIsChangingStatus(true)
    setActionError('')
    setSuccess('')

    try {
      const response = shouldDeactivate
        ? await deactivateStudent(student.id)
        : await activateStudent(student.id)

      setStatusStudent(null)

      try {
        await refreshStudents()
      } catch (refreshError) {
        setListError(
          getStudentErrorMessage(refreshError)
        )
      }

      setSuccess(
        response.detail
        || (
          shouldDeactivate
            ? 'Estudiante desactivado correctamente.'
            : 'Estudiante activado correctamente.'
        )
      )
    } catch (statusError) {
      setStatusStudent(null)
      setActionError(
        getStudentErrorMessage(statusError)
      )
    } finally {
      setIsChangingStatus(false)
    }
  }

  function handleFilterSubmit(event) {
    event.preventDefault()

    setFilters({
      search: searchInput,
      status: statusInput,
    })
  }

  function handleClearFilters() {
    setSearchInput('')
    setStatusInput('')
    setFilters({
      search: '',
      status: '',
    })
  }

  const statusAction = statusStudent?.is_active
    ? 'desactivar'
    : 'activar'

  return (
    <main className="students-page">
      <header className="students-page__header">
        <div>
          <p className="students-page__eyebrow">
            {pageEyebrow}
          </p>

          <h1>
            {pageTitle}
          </h1>

          <p className="students-page__description">
            {pageDescription || (
              canManageStudents
                ? (
                    'Consulta y gestiona la información '
                    + 'general de los estudiantes '
                    + 'atendidos por MIL-AL.'
                  )
                : (
                    'Consulta la información general de '
                    + 'los estudiantes asignados.'
                  )
            )}
          </p>
        </div>

        <div className="students-page__actions">
          {onChangeSpace && (
              <button
                className="button button--secondary"
                type="button"
                onClick={onChangeSpace}
                disabled={
                  isSubmitting
                  || isUpdating
                  || isChangingStatus
                }
              >
                Cambiar espacio
              </button>
            )}

          <button
            className="button button--secondary"
            type="button"
            onClick={onLogout}
            disabled={
              isSubmitting
              || isUpdating
              || isChangingStatus
            }
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      {success && (
        <div
          className="students-message students-message--success"
          role="status"
        >
          {success}
        </div>
      )}

      {actionError && (
        <div
          className="students-message students-message--error"
          role="alert"
        >
          {actionError}
        </div>
      )}

      <section
        className="students-card"
        aria-labelledby="students-list-title"
      >
        <div className="students-card__header">
          <h2 id="students-list-title">
            Estudiantes registrados
          </h2>

          <p>
            {students.length} estudiantes encontrados
          </p>
        </div>

        <div className="students-card__content">
          <form
            className="student-filters"
            onSubmit={handleFilterSubmit}
          >
            <div className="form-field">
              <label htmlFor="student-search">
                Buscar
              </label>

              <input
                id="student-search"
                type="search"
                value={searchInput}
                onChange={(event) => {
                  setSearchInput(event.target.value)
                }}
                placeholder="Código, nombres o apellidos"
              />
            </div>

            <div className="form-field">
              <label htmlFor="student-status">
                Estado
              </label>

              <select
                id="student-status"
                value={statusInput}
                onChange={(event) => {
                  setStatusInput(event.target.value)
                }}
              >
                <option value="">
                  Todos
                </option>

                <option value="active">
                  Activos
                </option>

                <option value="inactive">
                  Inactivos
                </option>
              </select>
            </div>

            <div className="student-filters__actions">
              <button
                className="button button--primary"
                type="submit"
              >
                Buscar
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
        </div>

        {listError && (
          <div
            className="students-message students-message--error"
            role="alert"
          >
            {listError}
          </div>
        )}

        {isLoading && (
          <div className="students-empty">
            Cargando estudiantes...
          </div>
        )}

        {!isLoading && !listError && (
          <StudentTable
            students={students}
            canManageStudents={canManageStudents}
            onEdit={handleEdit}
            onToggleStatus={handleToggleStatus}
            onManageAssignments={handleManageAssignments}
          />
        )}
      </section>

      {canManageStudents && (
        <section
          className="students-card students-card--registration"
          aria-labelledby="student-registration-title"
        >
          <div className="students-card__header">
            <h2 id="student-registration-title">
              Nuevo estudiante
            </h2>

            <p>
              Completa los datos obligatorios para
              realizar el registro.
            </p>
          </div>

          <div className="students-card__content">
            <StudentRegistrationForm
              key={formVersion}
              onSubmit={handleStudentSubmit}
              isSubmitting={isSubmitting}
              error={registrationError}
              success=""
            />
          </div>
        </section>
      )}

      {canManageStudents && assignmentStudent && (
        <Modal
          title="Asignaciones profesionales"
          onClose={handleAssignmentsClose}
        >
          <StudentAssignmentManager
            student={assignmentStudent}
          />
        </Modal>
      )}

      {canManageStudents && editingStudent && (
        <Modal
          title="Editar estudiante"
          onClose={handleEditCancel}
        >
          <StudentEditForm
            student={editingStudent}
            onSubmit={handleStudentUpdate}
            onCancel={handleEditCancel}
            isSubmitting={isUpdating}
            error={editError}
          />
        </Modal>
      )}

      {canManageStudents && statusStudent && (
        <ConfirmDialog
          title={
            statusStudent.is_active
              ? 'Desactivar estudiante'
              : 'Activar estudiante'
          }
          message={
            `¿Deseas ${statusAction} al estudiante `
            + `${statusStudent.first_name} `
            + `${statusStudent.last_name} `
            + `(${statusStudent.institutional_code})?`
          }
          confirmLabel={
            isChangingStatus
              ? 'Procesando...'
              : (
                statusStudent.is_active
                  ? 'Desactivar'
                  : 'Activar'
              )
          }
          onConfirm={handleStatusConfirm}
          onCancel={handleStatusCancel}
        />
      )}
    </main>
  )
}


export default StudentManagementPage