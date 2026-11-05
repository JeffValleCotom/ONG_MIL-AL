import {
  useEffect,
  useId,
} from 'react'

import './AppModal.css'


function AppModal({
  isOpen,
  title,
  subtitle = '',
  onClose,
  children,
  size = 'md',
  closeDisabled = false,
}) {
  const titleId = useId()

  useEffect(() => {
    if (!isOpen) {
      return undefined
    }

    const previousOverflow =
      document.body.style.overflow

    document.body.style.overflow = 'hidden'

    function handleKeyDown(event) {
      if (
        event.key === 'Escape'
        && !closeDisabled
      ) {
        onClose?.()
      }
    }

    document.addEventListener(
      'keydown',
      handleKeyDown,
    )

    return () => {
      document.body.style.overflow =
        previousOverflow

      document.removeEventListener(
        'keydown',
        handleKeyDown,
      )
    }
  }, [
    isOpen,
    onClose,
    closeDisabled,
  ])

  if (!isOpen) {
    return null
  }

  function handleBackdropClick(event) {
    if (
      event.target === event.currentTarget
      && !closeDisabled
    ) {
      onClose?.()
    }
  }

  return (
    <div
      className="app-modal"
      onMouseDown={handleBackdropClick}
      role="presentation"
    >
      <section
        className={
          `app-modal__panel app-modal__panel--${size}`
        }
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
      >
        <header className="app-modal__header">
          <div>
            <h2 id={titleId}>
              {title}
            </h2>

            {subtitle && (
              <p>{subtitle}</p>
            )}
          </div>

          <button
            className="app-modal__close"
            type="button"
            onClick={onClose}
            disabled={closeDisabled}
            aria-label="Cerrar ventana"
          >
            ×
          </button>
        </header>

        <div className="app-modal__content">
          {children}
        </div>
      </section>
    </div>
  )
}


export default AppModal
