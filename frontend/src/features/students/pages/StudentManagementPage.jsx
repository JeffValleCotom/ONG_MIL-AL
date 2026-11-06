import { useEffect, useState } from 'react'

import AppShell from '../../../components/layout/AppShell'
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
import StudentRecordPage
  from './StudentRecordPage'
import ReportManagementPage
  from '../../reports/pages/ReportManagementPage'
import DashboardPage
  from '../../dashboard/pages/DashboardPage'
import {
  activateStudent,
  createStudent,
  deactivateStudent,
  getStudents,
  updateStudent,
} from '../services/studentService'
import './StudentManagementPage.css'

const ROLE_LABELS = {
  RESPONSABLE_INSTITUCIONAL:
    'Gestión institucional',
  DOCENTE:
    'Espacio docente',
  PSICOLOGO:
    'Espacio psicológico',
  TERAPEUTA:
    'Espacio terapéutico',
}

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
  user,
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
  const [recordStudent, setRecordStudent] =
    useState(null)
  const [showReports, setShowReports] =
    useState(false)
  const [showDashboard, setShowDashboard] =
    useState(false)

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

  function handleViewRecord(student) {
    setShowReports(false)
    setShowDashboard(false)
    setRecordStudent(student)
    setActionError('')
    setSuccess('')
  }


  function handleRecordBack() {
    setRecordStudent(null)
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

  const roleLabel =
    ROLE_LABELS[studentContext]
    || pageEyebrow
    || 'ONG MIL-AL'

  const activeStudentCount = students.filter(
    (student) => student.is_active,
  ).length

  const inactiveStudentCount =
    students.length - activeStudentCount

  const navigationItems = [
    {
      id: 'students',
      label: 'Estudiantes',
      icon: 'students',
      active:
        !showReports
        && !showDashboard
        && !recordStudent,
      onClick: () => {
        setShowReports(false)
        setShowDashboard(false)
        setRecordStudent(null)
      },
    },
    {
      id: 'reports',
      label: 'Reportes',
      icon: 'reports',
      active: showReports,
      onClick: () => {
        setShowDashboard(false)
        setRecordStudent(null)
        setShowReports(true)
      },
    },
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'dashboard',
      active: showDashboard,
      onClick: () => {
        setShowReports(false)
        setRecordStudent(null)
        setShowDashboard(true)
      },
    },
  ]

    if (showDashboard) {
      return (
        <AppShell
          title="Dashboard"
          subtitle={
            'Indicadores y evolución del '
            + 'seguimiento estudiantil'
          }
          user={user}
          roleLabel={roleLabel}
          navigationItems={navigationItems}
          onChangeSpace={onChangeSpace}
          onLogout={onLogout}
        >
          <DashboardPage
            studentContext={studentContext}
          />
        </AppShell>
      )
    }

    if (showReports) {
      return (
        <AppShell
          title="Reportes"
          subtitle={
            'Generación y consulta de reportes '
            + 'de seguimiento'
          }
          user={user}
          roleLabel={roleLabel}
          navigationItems={navigationItems}
          onChangeSpace={onChangeSpace}
          onLogout={onLogout}
        >
          <ReportManagementPage
            students={students}
            studentContext={studentContext}
            embedded
            onBack={() => {
              setShowReports(false)
            }}
            onLogout={onLogout}
            onChangeSpace={onChangeSpace}
          />
        </AppShell>
      )
    }

    if (recordStudent) {
      const recordName = [
        recordStudent.first_name,
        recordStudent.last_name,
      ]
        .filter(Boolean)
        .join(' ')

      return (
        <AppShell
          title="Expediente del estudiante"
          subtitle={
            `${recordName} · `
            + recordStudent.institutional_code
          }
          user={user}
          roleLabel={roleLabel}
          navigationItems={navigationItems}
          onChangeSpace={onChangeSpace}
          onLogout={onLogout}
        >
          <StudentRecordPage
            studentId={recordStudent.id}
            studentContext={studentContext}
            onBack={handleRecordBack}
          />
        </AppShell>
      )
    }

  return (
    <AppShell
      title={pageTitle}
      subtitle={
        pageDescription
        || 'Gestión y seguimiento de estudiantes'
      }
      user={user}
      roleLabel={roleLabel}
      navigationItems={navigationItems}
      onChangeSpace={onChangeSpace}
      onLogout={onLogout}
    >
      <main className="students-page">

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

      <div className="students-overview">
        <article className="students-overview__item">
          <span className="students-overview__icon">
            ◫
          </span>

          <div>
            <strong>
              {students.length}
            </strong>

            <span>
              {canManageStudents
                ? 'Estudiantes registrados'
                : 'Estudiantes asignados'}
            </span>
          </div>
        </article>

        <article className="students-overview__item">
          <span className="students-overview__icon">
            ✓
          </span>

          <div>
            <strong>
              {activeStudentCount}
            </strong>

            <span>
              Estudiantes activos
            </span>
          </div>
        </article>

        <article
          className={
            'students-overview__item '
            + 'students-overview__item--neutral'
          }
        >
          <span className="students-overview__icon">
            ○
          </span>

          <div>
            <strong>
              {inactiveStudentCount}
            </strong>

            <span>
              Estudiantes inactivos
            </span>
          </div>
        </article>
      </div>

      <section
        className="students-card"
        aria-labelledby="students-list-title"
      >
        <div className="students-card__header">
          <div>
            <p className="students-card__eyebrow">
              Directorio estudiantil
            </p>

            <h2 id="students-list-title">
              {canManageStudents
                ? 'Estudiantes registrados'
                : 'Estudiantes asignados'}
            </h2>

            <p>
              Consulta los estudiantes disponibles
              en este espacio de trabajo.
            </p>
          </div>

          <span className="students-card__count">
            {students.length}{' '}
            {students.length === 1
              ? 'estudiante'
              : 'estudiantes'}
          </span>
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
                className="milal-button milal-button--primary"
                type="submit"
              >
                Buscar
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
            onViewRecord={handleViewRecord}
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
    </AppShell>
  )
}


export default StudentManagementPage