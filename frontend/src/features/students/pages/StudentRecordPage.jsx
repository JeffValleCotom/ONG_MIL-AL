import { useEffect, useState } from 'react'

import AcademicFollowUpForm
  from '../../academic/components/AcademicFollowUpForm'
import AcademicFollowUpList
  from '../../academic/components/AcademicFollowUpList'
import {
  createAcademicFollowUp,
  updateAcademicFollowUp,
} from '../../academic/services/academicService'
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


function getAcademicErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible guardar el seguimiento académico.'
    )
  }

  const fieldOrder = [
    'student_id',
    'followup_date',
    'academic_period',
    'subject',
    'observations',
    'strengths',
    'areas_for_improvement',
    'recommendations',
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
    || 'No fue posible guardar el seguimiento académico.'
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

  const [
    isAcademicFormOpen,
    setIsAcademicFormOpen,
  ] = useState(false)

  const [
    editingFollowUp,
    setEditingFollowUp,
  ] = useState(null)

  const [
    isSavingAcademic,
    setIsSavingAcademic,
  ] = useState(false)

  const [
    academicError,
    setAcademicError,
  ] = useState('')

  const [
    academicSuccess,
    setAcademicSuccess,
  ] = useState('')

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

  async function refreshRecord() {
    const data = await getStudentRecord(
      studentId,
      studentContext
    )

    setRecord(data)
  }

  function handleNewAcademicFollowUp() {
    setEditingFollowUp(null)
    setAcademicError('')
    setAcademicSuccess('')
    setIsAcademicFormOpen(true)
  }

  function handleAcademicEdit(followUp) {
    setEditingFollowUp(followUp)
    setAcademicError('')
    setAcademicSuccess('')
    setIsAcademicFormOpen(true)
  }

  function handleAcademicCancel() {
    if (isSavingAcademic) {
      return
    }

    setEditingFollowUp(null)
    setAcademicError('')
    setIsAcademicFormOpen(false)
  }

  async function handleAcademicSubmit(
    followUpData
  ) {
    if (isSavingAcademic) {
      return
    }

    const isEditing = Boolean(editingFollowUp)

    setIsSavingAcademic(true)
    setAcademicError('')
    setAcademicSuccess('')

    try {
      if (isEditing) {
        await updateAcademicFollowUp({
          followUpId: editingFollowUp.id,
          context: studentContext,
          followUpData,
        })
      } else {
        await createAcademicFollowUp({
          studentId,
          context: studentContext,
          followUpData,
        })
      }

      setEditingFollowUp(null)
      setIsAcademicFormOpen(false)

      setAcademicSuccess(
        isEditing
          ? 'Seguimiento académico actualizado correctamente.'
          : 'Seguimiento académico registrado correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setAcademicError(
          'El seguimiento fue guardado, pero no fue '
          + 'posible actualizar la vista del expediente.'
        )
      }
    } catch (saveError) {
      setAcademicError(
        getAcademicErrorMessage(saveError)
      )
    } finally {
      setIsSavingAcademic(false)
    }
  }

  const general = record?.sections?.general
  const academic = record?.sections?.academic

  const academicFollowUps =
    academic?.followups ?? []

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
          disabled={isSavingAcademic}
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
            className={
              'student-record-message '
              + 'student-record-message--error'
            }
            role="alert"
          >
            {error}
          </div>
        </section>
      )}

      {!isLoading && !error && general && (
        <>
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

          {academic && (
            <section
              className={
                'student-record-card '
                + 'student-record-card--academic'
              }
              aria-labelledby="academic-section-title"
            >
              <div
                className={
                  'student-record-card__header '
                  + 'student-record-card__header--actions'
                }
              >
                <div>
                  <h2 id="academic-section-title">
                    Información académica
                  </h2>

                  <p>
                    Historial de seguimiento académico
                    del estudiante.
                  </p>
                </div>

                {general.is_active
                  && !isAcademicFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={
                      handleNewAcademicFollowUp
                    }
                  >
                    Registrar seguimiento
                  </button>
                )}
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se
                  pueden registrar nuevos seguimientos
                  académicos.
                </div>
              )}

              {academicSuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-academic-message'
                  }
                  role="status"
                >
                  {academicSuccess}
                </div>
              )}

              {academicError
                && !isAcademicFormOpen && (
                <div
                  className={
                    'form-message '
                    + 'form-message--error '
                    + 'student-record-academic-message'
                  }
                  role="alert"
                >
                  {academicError}
                </div>
              )}

              {isAcademicFormOpen && (
                <div className="student-record-card__content">
                  <h3 className="student-record-form-title">
                    {editingFollowUp
                      ? 'Editar seguimiento académico'
                      : 'Nuevo seguimiento académico'}
                  </h3>

                  <AcademicFollowUpForm
                    key={
                      editingFollowUp
                        ? `edit-${editingFollowUp.id}`
                        : 'new'
                    }
                    initialFollowUp={
                      editingFollowUp
                    }
                    onSubmit={
                      handleAcademicSubmit
                    }
                    onCancel={
                      handleAcademicCancel
                    }
                    isSubmitting={
                      isSavingAcademic
                    }
                    error={academicError}
                  />
                </div>
              )}

              <AcademicFollowUpList
                followups={academicFollowUps}
                onEdit={handleAcademicEdit}
              />
            </section>
          )}
        </>
      )}
    </main>
  )
}


export default StudentRecordPage
