function Modal({
  title,
  children,
  onClose,
}) {
  return (
    <div
      className="modal-backdrop"
      role="presentation"
    >
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <header className="modal__header">
          <h2 id="modal-title">
            {title}
          </h2>

          <button
            className="modal__close"
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
          >
            ×
          </button>
        </header>

        <div className="modal__body">
          {children}
        </div>
      </section>
    </div>
  )
}

export default Modal