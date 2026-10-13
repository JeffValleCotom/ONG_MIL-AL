function getFullName(user) {
  const fullName = `${user.first_name} ${user.last_name}`.trim()

  return fullName || user.username
}

function UserTable({
  users,
  onEdit,
  onManageRoles,
  onToggleStatus,
}) {
  if (users.length === 0) {
    return (
      <div className="users-empty">
        No hay usuarios registrados.
      </div>
    )
  }

  return (
    <div className="table-container">
      <table className="users-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Correo</th>
            <th>Roles</th>
            <th>Estado</th>
            <th>
              <span className="sr-only">
                Acciones
              </span>
            </th>
          </tr>
        </thead>

        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>
                <div className="user-identity">
                  <strong>{getFullName(user)}</strong>
                  <span>@{user.username}</span>
                </div>
              </td>

              <td>
                {user.email || 'Sin correo'}
              </td>

              <td>
                <div className="role-list">
                  {user.roles.length > 0 ? (
                    user.roles.map((role) => (
                      <span
                        className="role-badge"
                        key={role}
                      >
                        {role}
                      </span>
                    ))
                  ) : (
                    <span>Sin rol</span>
                  )}
                </div>
              </td>

              <td>
                <span
                  className={
                    user.is_active
                      ? 'status status--active'
                      : 'status status--inactive'
                  }
                >
                  {user.is_active
                    ? 'Activo'
                    : 'Inactivo'}
                </span>
              </td>

              <td>
                <div className="user-actions">
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => onEdit?.(user)}
                  >
                    Editar
                  </button>

                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={() => onManageRoles?.(user)}
                  >
                    Roles
                  </button>

                  <button
                    className="button button--danger"
                    type="button"
                    onClick={() => onToggleStatus?.(user)}
                  >
                    {user.is_active
                      ? 'Desactivar'
                      : 'Activar'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default UserTable
