import { useState } from 'react'

import StudentRegistrationForm
  from '../components/StudentRegistrationForm'
import { createStudent } from '../services/studentService'
import './StudentManagementPage.css'


function getStudentErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message ||
      'No fue posible registrar al estudiante.'
    )
  }

  const fieldOrder = [
    'institutional_code',
    'first_name',
    'last_name',
    'date_of_birth',
    'admission_date',
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
    'No fue posible registrar al estudiante.'
  )
}


function StudentManagementPage({
  onLogout,
}) {
  const [isSubmitting, setIsSubmitting] =
    useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formVersion, setFormVersion] =
    useState(0)

  async function handleStudentSubmit(studentData) {
    setIsSubmitting(true)
    setError('')
    setSuccess('')

    try {
      const student = await createStudent(
        studentData
      )

      setSuccess(
        `Estudiante ${student.institutional_code} `
        + 'registrado correctamente.'
      )

      setFormVersion((current) => current + 1)
    } catch (registrationError) {
      setError(
        getStudentErrorMessage(
          registrationError
        )
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="students-page">
      <header className="students-page__header">
        <div>
          <p className="students-page__eyebrow">
            Gestión de estudiantes
          </p>

          <h1>
            Registro de estudiantes
          </h1>

          <p className="students-page__description">
            Registra la información general del
            estudiante para iniciar su expediente
            institucional en MIL-AL.
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
            error={error}
            success={success}
          />
        </div>
      </section>
    </main>
  )
}


export default StudentManagementPage
