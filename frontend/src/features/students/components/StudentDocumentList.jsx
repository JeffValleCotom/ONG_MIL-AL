function formatFileSize(value) {
  const bytes = Number(value)

  if (!Number.isFinite(bytes) || bytes < 0) {
    return '—'
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(
    bytes / (1024 * 1024)
  ).toFixed(1)} MB`
}


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


function StudentDocumentList({
  documents = [],
  isLoading = false,
  onDownload,
  downloadingId = null,
}) {
  if (isLoading) {
    return (
      <div className="student-record-message">
        Cargando documentos...
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="student-record-message">
        No hay documentos disponibles para este contexto.
      </div>
    )
  }

  return (
    <div className="student-document-list">
      {documents.map((documentItem) => (
        <article
          key={documentItem.id}
          className="student-document-item"
        >
          <div className="student-document-item__content">
            <h3>
              {documentItem.document_type_display}
            </h3>

            {documentItem.document_type_detail && (
              <p>
                {documentItem.document_type_detail}
              </p>
            )}

            <p>
              <strong>Archivo:</strong>{' '}
              {documentItem.original_filename}
            </p>

            <p>
              <strong>Tipo MIME:</strong>{' '}
              {documentItem.mime_type}
            </p>

            <p>
              <strong>Tamaño:</strong>{' '}
              {formatFileSize(
                documentItem.size_bytes
              )}
            </p>

            {documentItem.description && (
              <p>
                <strong>Descripción:</strong>{' '}
                {documentItem.description}
              </p>
            )}

            <p>
              <strong>Cargado:</strong>{' '}
              {formatDateTime(
                documentItem.created_at
              )}
            </p>

            {!documentItem.is_active && (
              <p>
                <strong>Estado:</strong> Inactivo
              </p>
            )}
          </div>

          <div className="student-document-item__actions">
            <button
              className="button button--secondary"
              type="button"
              onClick={() => {
                onDownload(documentItem)
              }}
              disabled={
                downloadingId === documentItem.id
              }
            >
              {downloadingId === documentItem.id
                ? 'Descargando...'
                : 'Descargar'}
            </button>
          </div>
        </article>
      ))}
    </div>
  )
}


export default StudentDocumentList
