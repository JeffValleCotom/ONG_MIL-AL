import milalLogo
  from '../../../assets/ong-milal-logo.png'

import './RoleSpaceSelectorPage.css'


function getUserDisplayName(user) {
  const fullName = [
    user?.first_name,
    user?.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return fullName || user?.username || 'Usuario'
}


function SpaceIcon({ role }) {
  const commonProps = {
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': true,
  }

  if (role === 'ADMINISTRADOR') {
    return (
      <svg {...commonProps}>
        <path d="M12 3 4 7v5c0 5 3.4 8 8 9 4.6-1 8-4 8-9V7l-8-4Z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    )
  }

  if (role === 'RESPONSABLE_INSTITUCIONAL') {
    return (
      <svg {...commonProps}>
        <path d="M3 21h18" />
        <path d="M5 21V9l7-5 7 5v12" />
        <path d="M9 21v-6h6v6" />
      </svg>
    )
  }

  if (role === 'DOCENTE') {
    return (
      <svg {...commonProps}>
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M4 4h16v16H6.5A2.5 2.5 0 0 1 4 17.5Z" />
        <path d="M8 8h8" />
        <path d="M8 12h5" />
      </svg>
    )
  }

  if (role === 'PSICOLOGO') {
    return (
      <svg {...commonProps}>
        <path d="M12 21a9 9 0 1 0-9-9" />
        <path d="M3 12h6" />
        <path d="M6 9v6" />
        <path d="M14 9h.01" />
        <path d="M17 12h.01" />
        <path d="M14 15h.01" />
      </svg>
    )
  }

  if (role === 'TERAPEUTA') {
    return (
      <svg {...commonProps}>
        <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10Z" />
      </svg>
    )
  }

  return (
    <svg {...commonProps}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9 12h6" />
      <path d="m12 9 3 3-3 3" />
    </svg>
  )
}


function RoleSpaceSelectorPage({
  user,
  spaces,
  onSelect,
  onLogout,
}) {
  return (
    <main className="space-selector-page">
      <header className="space-selector-topbar">
        <div className="space-selector-brand">
          <img
            src={milalLogo}
            alt="ONG MIL-AL"
          />

          <div>
            <strong>ONG MIL-AL</strong>
            <span>
              Plataforma de Seguimiento Estudiantil
            </span>
          </div>
        </div>

        <div className="space-selector-session">
          <div className="space-selector-session__user">
            <span>Sesión iniciada como</span>

            <strong>
              {getUserDisplayName(user)}
            </strong>
          </div>

          <button
            className="space-selector-logout"
            type="button"
            onClick={onLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      <section className="space-selector-content">
        <div className="space-selector-heading">
          <p className="space-selector-heading__eyebrow">
            Espacio de trabajo
          </p>

          <h1>
            ¿Dónde deseas trabajar?
          </h1>

          <p>
            Tu cuenta tiene acceso a más de un espacio
            funcional. Selecciona el contexto que deseas
            utilizar.
          </p>
        </div>

        {spaces.length > 0 ? (
          <div className="space-selector-grid">
            {spaces.map((space) => (
              <button
                key={space.role}
                className="space-selector-option"
                type="button"
                onClick={() => onSelect(space.role)}
              >
                <span className="space-selector-option__icon">
                  <SpaceIcon role={space.role} />
                </span>

                <span className="space-selector-option__content">
                  <strong>
                    {space.label}
                  </strong>

                  <span>
                    {space.description}
                  </span>
                </span>

                <span
                  className="space-selector-option__arrow"
                  aria-hidden="true"
                >
                  →
                </span>
              </button>
            ))}
          </div>
        ) : (
          <div
            className="space-selector-empty"
            role="alert"
          >
            <strong>
              No hay espacios disponibles
            </strong>

            <span>
              Tu cuenta no tiene un espacio funcional
              habilitado en la plataforma.
            </span>
          </div>
        )}
      </section>

      <footer className="space-selector-footer">
        <span>
          ONG MIL-AL
        </span>

        <span aria-hidden="true">·</span>

        <span>
          Acceso exclusivo para personal autorizado
        </span>
      </footer>

      <div
        className="space-selector-decoration"
        aria-hidden="true"
      >
        <span className="space-selector-decoration__green" />
        <span className="space-selector-decoration__red" />
      </div>
    </main>
  )
}


export default RoleSpaceSelectorPage
