import { useMemo, useState } from 'react'


const DOCUMENT_TYPES_BY_CONTEXT = {
  DOCENTE: [
    {
      value: 'ACADEMICO',
      label: 'Académico',
    },
  ],
  PSICOLOGO: [
    {
      value: 'PSICOLOGICO',
      label: 'Psicológico',
    },
  ],
  TERAPEUTA: [
    {
      value: 'TERAPEUTICO',
      label: 'Terapéutico',
    },
  ],
  RESPONSABLE_INSTITUCIONAL: [
    {
      value: 'IDENTIFICACION',
      label: 'Identificación',
    },
    {
      value: 'CONSENTIMIENTO_AUTORIZACION',
      label: 'Consentimiento o autorización',
    },
    {
      value: 'MEDICO',
      label: 'Médico',
    },
    {
      value: 'INSTITUCIONAL',
      label: 'Institucional',
    },
    {
      value: 'OTRO',
      label: 'Otro',
    },
  ],
}


function StudentDocumentUploadForm({
  context,
  onSubmit,
  onCancel,
  isSubmitting = false,
  error = '',
}) {
  const availableTypes = useMemo(
    () => (
      DOCUMENT_TYPES_BY_CONTEXT[context] ?? []
    ),
    [context]
  )

  const [documentType, setDocumentType] = useState(
    availableTypes[0]?.value ?? ''
  )

  const [
    documentTypeDetail,
    setDocumentTypeDetail,
  ] = useState('')

  const [description, setDescription] = useState('')
  const [file, setFile] = useState(null)

  function handleSubmit(event) {
    event.preventDefault()

    if (
      isSubmitting
      || !documentType
      || !file
    ) {
      return
    }

    onSubmit({
      documentType,
      documentTypeDetail:
        documentType === 'OTRO'
          ? documentTypeDetail.trim()
          : '',
      description: description.trim(),
      file,
    })
  }

  if (availableTypes.length === 0) {
    return (
      <div
        className="form-message form-message--error"
        role="alert"
      >
        El contexto actual no permite cargar documentos.
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div
          className="form-message form-message--error"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="form-field">
        <label htmlFor="student-document-type">
          Tipo de documento
        </label>

        <select
          id="student-document-type"
          value={documentType}
          onChange={(event) => {
            const value = event.target.value

            setDocumentType(value)

            if (value !== 'OTRO') {
              setDocumentTypeDetail('')
            }
          }}
          disabled={isSubmitting}
          required
        >
          {availableTypes.map((type) => (
            <option
              key={type.value}
              value={type.value}
            >
              {type.label}
            </option>
          ))}
        </select>
      </div>

      {documentType === 'OTRO' && (
        <div className="form-field">
          <label htmlFor="student-document-type-detail">
            Especifique el tipo
          </label>

          <input
            id="student-document-type-detail"
            type="text"
            maxLength={150}
            value={documentTypeDetail}
            onChange={(event) => {
              setDocumentTypeDetail(
                event.target.value
              )
            }}
            disabled={isSubmitting}
            required
          />
        </div>
      )}

      <div className="form-field">
        <label htmlFor="student-document-description">
          Descripción
        </label>

        <textarea
          id="student-document-description"
          value={description}
          onChange={(event) => {
            setDescription(event.target.value)
          }}
          disabled={isSubmitting}
        />
      </div>

      <div className="form-field">
        <label htmlFor="student-document-file">
          Archivo
        </label>

        <input
          id="student-document-file"
          type="file"
          onChange={(event) => {
            setFile(
              event.target.files?.[0] ?? null
            )
          }}
          disabled={isSubmitting}
          required
        />
      </div>

      <div className="form-actions">
        <button
          className="button button--primary"
          type="submit"
          disabled={
            isSubmitting
            || !file
            || (
              documentType === 'OTRO'
              && !documentTypeDetail.trim()
            )
          }
        >
          {isSubmitting
            ? 'Cargando...'
            : 'Cargar documento'}
        </button>

        <button
          className="button button--secondary"
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}


export default StudentDocumentUploadForm
