import { useEffect, useState } from 'react'

import { getStudentRecord }
  from '../services/studentService'
import './StudentRecordPage.css'


function formatDate(value) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}/${month}/${year}`
}


function getRecordErrorMessage(error) {
  const data = error?.data

  if (data?.context) {
    const value = data.context

    if (Array.isArray(value)) {
      return value[0]
    }

    if (typeof value === 'string') {
      return value
    }
  }

  return (
    data?.detail
    || error?.message
    || 'No fue posible cargar el expediente.'
  )
}


function StudentRecordPage({
  studentId,
  studentContext,
  onBack,
}) {
  const [record, setRecord] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isMounted = true

    async function loadRecord() {
      setIsLoading(true)
      setError('')

      try {
        const data = await getStudentRecord(
          studentId,
          studentContext
        )

        if (isMounted) {
          setRecord(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            getRecordErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadRecord()

    return () => {
      isMounted = false
    }
  }, [studentId, studentContext])

  const general = record?.sections?.general

  return (
    <main className="student-record-page">
      <header className="student-record-page__header">
        <div>
          <p className="student-record-page__eyebrow">
            Expediente individual
          </p>

          <h1>
            {general
              ? `${general.first_name} ${general.last_name}`
              : 'Expediente del estudiante'}
          </h1>

          {record && (
            <p className="student-record-page__description">
              Contexto de consulta: {record.context}
            </p>
          )}
        </div>

        <button
          className="button button--secondary"
          type="button"
          onClick={onBack}
        >
          Volver a estudiantes
        </button>
      </header>

      {isLoading && (
        <section className="student-record-card">
          <div className="student-record-message">
            Cargando expediente...
          </div>
        </section>
      )}

      {!isLoading && error && (
        <section className="student-record-card">
          <div
            className="student-record-message student-record-message--error"
            role="alert"
          >
            {error}
          </div>
        </section>
      )}

      {!isLoading && !error && general && (
        <section
          className="student-record-card"
          aria-labelledby="general-section-title"
        >
          <div className="student-record-card__header">
            <h2 id="general-section-title">
              Información general
            </h2>

            <p>
              Datos institucionales base del estudiante.
            </p>
          </div>

          <dl className="student-record-grid">
            <div>
              <dt>Código institucional</dt>
              <dd>
                {general.institutional_code}
              </dd>
            </div>

            <div>
              <dt>Nombres</dt>
              <dd>{general.first_name}</dd>
            </div>

            <div>
              <dt>Apellidos</dt>
              <dd>{general.last_name}</dd>
            </div>

            <div>
              <dt>Fecha de nacimiento</dt>
              <dd>
                {formatDate(
                  general.date_of_birth
                )}
              </dd>
            </div>

            <div>
              <dt>Fecha de ingreso</dt>
              <dd>
                {formatDate(
                  general.admission_date
                )}
              </dd>
            </div>

            <div>
              <dt>Estado</dt>
              <dd>
                <span
                  className={
                    general.is_active
                      ? 'status status--active'
                      : 'status status--inactive'
                  }
                >
                  {general.is_active
                    ? 'Activo'
                    : 'Inactivo'}
                </span>
              </dd>
            </div>
          </dl>
        </section>
      )}
    </main>
  )
}


export default StudentRecordPage