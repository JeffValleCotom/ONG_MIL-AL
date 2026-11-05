import milalLogo
  from '../../assets/ong-milal-logo.png'


function SidebarIcon({
  name,
}) {
  const commonProps = {
    width: 21,
    height: 21,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': true,
  }

  if (name === 'home') {
    return (
      <svg {...commonProps}>
        <path d="M3 11.5 12 4l9 7.5" />
        <path d="M5 10v10h14V10" />
        <path d="M9 20v-6h6v6" />
      </svg>
    )
  }

  if (name === 'students') {
    return (
      <svg {...commonProps}>
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    )
  }

  if (name === 'reports') {
    return (
      <svg {...commonProps}>
        <path d="M4 19V9" />
        <path d="M10 19V5" />
        <path d="M16 19v-7" />
        <path d="M22 19V3" />
      </svg>
    )
  }

  if (name === 'ai') {
    return (
      <svg {...commonProps}>
        <path d="m12 3-1.1 3.1A7 7 0 0 1 6.6 10L3 11l3.6 1a7 7 0 0 1 4.3 3.9L12 19l1.1-3.1a7 7 0 0 1 4.3-3.9l3.6-1-3.6-1a7 7 0 0 1-4.3-3.9L12 3Z" />
      </svg>
    )
  }

  if (name === 'interventions') {
    return (
      <svg {...commonProps}>
        <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z" />
      </svg>
    )
  }

  if (name === 'alerts') {
    return (
      <svg {...commonProps}>
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M13.7 21a2 2 0 0 1-3.4 0" />
      </svg>
    )
  }

  if (name === 'users') {
    return (
      <svg {...commonProps}>
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21a8 8 0 0 1 16 0" />
      </svg>
    )
  }

  if (name === 'user-plus') {
    return (
        <svg {...commonProps}>
        <path d="M15 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8" cy="7" r="4" />
        <path d="M19 8v6" />
        <path d="M16 11h6" />
        </svg>
    )
    }

    if (name === 'key') {
    return (
        <svg {...commonProps}>
        <circle cx="8" cy="15" r="4" />
        <path d="m11 12 8-8" />
        <path d="m17 6 2 2" />
        <path d="m15 8 2 2" />
        </svg>
    )
    }

  return (
    <svg {...commonProps}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9 12h6" />
    </svg>
  )
}


export default function AppSidebar({
  items = [],
  onClose,
}) {
  return (
    <aside className="milal-sidebar">
      <div className="milal-sidebar__brand">
        <img
          className="milal-sidebar__logo"
          src={milalLogo}
          alt="ONG MIL-AL"
        />

        <div className="milal-sidebar__brand-copy">
          <strong>ONG MIL-AL</strong>

          <span>
            Plataforma de Seguimiento
            Estudiantil
          </span>
        </div>

        <button
          className="milal-sidebar__mobile-close"
          type="button"
          aria-label="Cerrar menú"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <div className="milal-sidebar__divider" />

      <nav
        className="milal-sidebar__navigation"
        aria-label="Navegación principal"
      >
        {items.map((item) => (
          <button
            key={item.id}
            className={[
                'milal-sidebar__item',
                item.active
                    ? 'milal-sidebar__item--active'
                    : '',
                item.secondary
                    ? 'milal-sidebar__item--secondary'
                    : '',
                ]
                .filter(Boolean)
                .join(' ')}

            type="button"
            onClick={() => {
              item.onClick?.()
              onClose?.()
            }}
          >
            <span className="milal-sidebar__item-icon">
              <SidebarIcon
                name={item.icon}
              />
            </span>

            <span className="milal-sidebar__item-label">
              {item.label}
            </span>

            {item.badge !== undefined
              && item.badge !== null
              && (
                <span className="milal-sidebar__badge">
                  {item.badge}
                </span>
              )}
          </button>
        ))}
      </nav>

      <div className="milal-sidebar__decoration">
        <span className="milal-sidebar__curve milal-sidebar__curve--green" />
        <span className="milal-sidebar__curve milal-sidebar__curve--red" />
      </div>
    </aside>
  )
}
