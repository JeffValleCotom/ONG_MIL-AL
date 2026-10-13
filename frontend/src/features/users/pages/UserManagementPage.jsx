import { useState } from 'react'

import Modal from '../../../components/Modal'
import UserForm from '../components/UserForm'
import UserTable from '../components/UserTable'
import './UserManagementPage.css'
import UserRoleForm from '../components/UserRoleForm'
import ConfirmDialog from '../../../components/ConfirmDialog'

const sampleUsers = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@milal.org.gt',
    first_name: 'Administrador',
    last_name: 'MIL-AL',
    roles: ['ADMINISTRADOR'],
    is_active: true,
  },
  {
    id: 2,
    username: 'docente',
    email: 'docente@milal.org.gt',
    first_name: 'Usuario',
    last_name: 'Docente',
    roles: ['DOCENTE'],
    is_active: true,
  },
  {
    id: 3,
    username: 'psicologia',
    email: 'psicologia@milal.org.gt',
    first_name: 'Usuario',
    last_name: 'Psicología',
    roles: ['PSICOLOGO'],
    is_active: false,
  },
]

function UserManagementPage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [roleUser, setRoleUser] = useState(null)
  const [statusUser, setStatusUser] = useState(null)

  function openCreateForm() {
    setRoleUser(null)
    setStatusUser(null)
    setSelectedUser(null)
    setIsFormOpen(true)
  }

  function openEditForm(user) {
    setRoleUser(null)
    setStatusUser(null)
    setSelectedUser(user)
    setIsFormOpen(true)
  }

  function closeForm() {
    setIsFormOpen(false)
    setSelectedUser(null)
  }

  function handleFormSubmit() {
    closeForm()
  }

  function openRoleForm(user) {
  setIsFormOpen(false)
  setSelectedUser(null)
  setStatusUser(null)
  setRoleUser(user)
  }

  function closeRoleForm() {
    setRoleUser(null)
  }

  function handleRoleSubmit() {
    closeRoleForm()
  }

  function openStatusConfirm(user) {
  setIsFormOpen(false)
  setSelectedUser(null)
  setRoleUser(null)
  setStatusUser(user)
  }

  function closeStatusConfirm() {
    setStatusUser(null)
  }

  function handleStatusConfirm() {
    closeStatusConfirm()
  }

  return (
    <main className="users-page">
      <header className="users-page__header">
        <div>
          <p className="users-page__eyebrow">
            Administración
          </p>

          <h1>
            Gestión de usuarios y roles
          </h1>

          <p className="users-page__description">
            Administra las cuentas institucionales,
            sus roles y su estado dentro de la
            plataforma MIL-AL.
          </p>
        </div>

        <button
          className="button button--primary"
          type="button"
          onClick={openCreateForm}
        >
          Nuevo usuario
        </button>
      </header>

      <section
        className="users-card"
        aria-labelledby="users-table-title"
      >
        <div className="users-card__header">
          <div>
            <h2 id="users-table-title">
              Usuarios institucionales
            </h2>

            <p>
              {sampleUsers.length} usuarios registrados
            </p>
          </div>
        </div>

        <UserTable
          users={sampleUsers}
          onEdit={openEditForm}
          onManageRoles={openRoleForm}
          onToggleStatus={openStatusConfirm}
        />
      </section>

      {isFormOpen && (
        <Modal
          title={
            selectedUser
              ? 'Editar usuario'
              : 'Nuevo usuario'
          }
          onClose={closeForm}
        >

          <UserForm
            key={selectedUser?.id ?? 'new-user'}
            user={selectedUser}
            onSubmit={handleFormSubmit}
            onCancel={closeForm}
          />
        </Modal>
      )}

      {roleUser && (
        <Modal
          title="Asignar roles"
          onClose={closeRoleForm}
        >
          <UserRoleForm
            key={roleUser.id}
            user={roleUser}
            onSubmit={handleRoleSubmit}
            onCancel={closeRoleForm}
          />
        </Modal>
      )}

      {statusUser && (
      
      <ConfirmDialog
        title={
          statusUser.is_active
            ? 'Desactivar usuario'
            : 'Activar usuario'
        }
        message={
          statusUser.is_active
            ? `¿Deseas desactivar al usuario ${statusUser.username}?`
            : `¿Deseas activar al usuario ${statusUser.username}?`
        }
        confirmLabel={
          statusUser.is_active
            ? 'Desactivar'
            : 'Activar'
        }
        onConfirm={handleStatusConfirm}
        onCancel={closeStatusConfirm}
      />
    )}

    </main>
  )
}

export default UserManagementPage