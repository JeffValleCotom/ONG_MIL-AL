import Modal from './Modal'

function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Confirmar',
  onConfirm,
  onCancel,
}) {
  return (
    <Modal
      title={title}
      onClose={onCancel}
    >
      <div className="confirm-dialog">
        <p>{message}</p>

        <div className="form-actions">
          <button
            className="button button--secondary"
            type="button"
            onClick={onCancel}
          >
            Cancelar
          </button>

          <button
            className="button button--danger"
            type="button"
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  )
}

export default ConfirmDialog