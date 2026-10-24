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


function RoleSpaceSelectorPage({
  user,
  spaces,
  onSelect,
  onLogout,
}) {
  return (
    <main className="space-selector-page">
      <section className="space-selector-card">
        <header className="space-selector-card__header">
          <p className="space-selector-card__eyebrow">
            ONG MIL-AL
          </p>

          <h1>Selecciona tu espacio de trabajo</h1>

          <p>
            Sesión iniciada como{' '}
            <strong>
              {getUserDisplayName(user)}
            </strong>.
          </p>
        </header>

        {spaces.length > 0 ? (
          <>
            <p className="space-selector-card__description">
              Tu cuenta posee más de un contexto funcional.
              Selecciona el espacio en el que deseas trabajar.
            </p>

            <div className="space-selector-grid">
              {spaces.map((space) => (
                <button
                  key={space.role}
                  className="space-selector-option"
                  type="button"
                  onClick={() => onSelect(space.role)}
                >
                  <strong>{space.label}</strong>

                  <span>{space.description}</span>
                </button>
              ))}
            </div>
          </>
        ) : (
          <div
            className="space-selector-empty"
            role="alert"
          >
            Tu cuenta no tiene un espacio funcional
            habilitado en la plataforma.
          </div>
        )}

        <div className="space-selector-card__actions">
          <button
            className="space-selector-logout"
            type="button"
            onClick={onLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </section>
    </main>
  )
}


export default RoleSpaceSelectorPage
