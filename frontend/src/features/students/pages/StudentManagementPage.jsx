import { useEffect, useState } from 'react'

import StudentRegistrationForm
  from '../components/StudentRegistrationForm'
import StudentTable
  from '../components/StudentTable'
import {
  createStudent,
  getStudents,
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
  canManageStudents = false,
}) {
  const [students, setStudents] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [listError, setListError] = useState('')
  const [registrationError, setRegistrationError] =
    useState('')
  const [success, setSuccess] = useState('')

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

  useEffect(() => {
    let isMounted = true

    async function loadStudents() {
      setIsLoading(true)
      setListError('')

      try {
        const data = await getStudents(filters)

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
  }, [filters])

  async function refreshStudents() {
    const data = await getStudents(filters)
    setStudents(data)
  }

  async function handleStudentSubmit(studentData) {
    setIsSubmitting(true)
    setRegistrationError('')
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

  return (
    <main className="students-page">
      <header className="students-page__header">
        <div>
          <p className="students-page__eyebrow">
            Gestión de estudiantes
          </p>

          <h1>
            Estudiantes
          </h1>

          <p className="students-page__description">
            {canManageStudents
              ? (
                'Consulta y registra la información '
                + 'general de los estudiantes '
                + 'atendidos por MIL-AL.'
              )
              : (
                'Consulta la información general de '
                + 'los estudiantes atendidos por '
                + 'MIL-AL.'
              )}
          </p>
        </div>

        <div className="students-page__actions">
          <button
            className="button button--secondary"
            type="button"
            onClick={onLogout}
            disabled={isSubmitting}
          >
            Cerrar sesión
          </button>
        </div>
      </header>

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
              success={success}
            />
          </div>
        </section>
      )}
    </main>
  )
}


export default StudentManagementPage