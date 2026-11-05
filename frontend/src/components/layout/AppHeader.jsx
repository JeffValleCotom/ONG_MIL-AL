function getUserDisplayName(user) {
  if (!user) {
    return 'Usuario'
  }

  const fullName = [
    user.first_name,
    user.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return (
    fullName
    || user.username
    || 'Usuario'
  )
}


function getUserInitials(user) {
  const displayName = (
    getUserDisplayName(user)
  )

  const parts = displayName
    .split(/\s+/)
    .filter(Boolean)

  if (parts.length === 1) {
    return parts[0]
      .slice(0, 2)
      .toUpperCase()
  }

  return (
    `${parts[0][0]}${parts[1][0]}`
      .toUpperCase()
  )
}


export default function AppHeader({
  title,
  subtitle,
  user,
  roleLabel,
  onMenuOpen,
  onChangeSpace,
  onLogout,
}) {
  return (
    <header className="milal-header">
      <div className="milal-header__title-group">
        <button
          className="milal-header__menu-button"
          type="button"
          aria-label="Abrir navegación"
          onClick={onMenuOpen}
        >
          <span />
          <span />
          <span />
        </button>

        <div className="milal-header__title-accent" />

        <div>
          <h1>{title}</h1>

          {subtitle && (
            <p>{subtitle}</p>
          )}
        </div>
      </div>

      <div className="milal-header__actions">
        {onChangeSpace && (
          <button
            className={
              'milal-header__secondary-action'
            }
            type="button"
            onClick={onChangeSpace}
          >
            Cambiar espacio
          </button>
        )}

        <div className="milal-header__profile">
          <div
            className="milal-header__avatar"
            aria-hidden="true"
          >
            {getUserInitials(user)}
          </div>

          <div className="milal-header__profile-copy">
            <strong>
              {getUserDisplayName(user)}
            </strong>

            <span>
              {roleLabel}
            </span>
          </div>
        </div>

        {onLogout && (
          <button
            className="milal-header__logout"
            type="button"
            onClick={onLogout}
          >
            Cerrar sesión
          </button>
        )}
      </div>
    </header>
  )
}
