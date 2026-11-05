import { useEffect, useState } from 'react'
import {
  activateUser,
  createUser,
  deactivateUser,
  getUsers,
  updateUser,
  updateUserRoles,
} from '../services/userService'

import Modal from '../../../components/Modal'
import UserForm from '../components/UserForm'
import UserTable from '../components/UserTable'
import './UserManagementPage.css'
import UserRoleForm from '../components/UserRoleForm'
import ConfirmDialog from '../../../components/ConfirmDialog'
import PasswordChangeForm
  from '../../auth/components/PasswordChangeForm'
import {
  changePassword,
} from '../../auth/services/authService'
import AppShell from '../../../components/layout/AppShell'

function UserManagementPage({
  user,
  onLogout,
  onChangeSpace,
}) {
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [roleUser, setRoleUser] = useState(null)
  const [statusUser, setStatusUser] = useState(null)
  const [isPasswordChangeOpen, setIsPasswordChangeOpen] =
  useState(false)
  const [isChangingPassword, setIsChangingPassword] =
    useState(false)
  const [passwordChangeError, setPasswordChangeError] =
    useState('')
  const [passwordChangeSuccess, setPasswordChangeSuccess] =
    useState('')

  useEffect(() => {
  let isMounted = true

  async function fetchUsers() {
    try {
      const data = await getUsers()

      if (isMounted) {
        setUsers(data)
      }
    } catch (loadError) {
      if (isMounted) {
        setError(
          loadError.message ||
            'No fue posible cargar los usuarios.'
        )
      }
    } finally {
      if (isMounted) {
        setIsLoading(false)
      }
    }
  }

  fetchUsers()

  return () => {
    isMounted = false
  }
}, [])

  function openCreateForm() {
    closePasswordChange()
    setRoleUser(null)
    setStatusUser(null)
    setSelectedUser(null)
    setIsFormOpen(true)
  }

  function openEditForm(user) {
    closePasswordChange()
    setRoleUser(null)
    setStatusUser(null)
    setSelectedUser(user)
    setIsFormOpen(true)
  }

  function closeForm() {
    setIsFormOpen(false)
    setSelectedUser(null)
  }

  async function handleFormSubmit(formData) {
  setError('')

  try {
    if (selectedUser) {
      const updateData = {
        ...formData,
      }

      if (!updateData.password) {
        delete updateData.password
      }

      await updateUser(
        selectedUser.id,
        updateData
      )
    } else {
      await createUser(formData)
    }

    const updatedUsers = await getUsers()
    setUsers(updatedUsers)

    closeForm()
  } catch (submitError) {
    setError(
      submitError.message ||
        'No fue posible guardar el usuario.'
    )
  }
}

  function openRoleForm(user) {
    closePasswordChange()
    setIsFormOpen(false)
    setSelectedUser(null)
    setStatusUser(null)
    setRoleUser(user)
  }

  function closeRoleForm() {
    setRoleUser(null)
  }

  async function handleRoleSubmit(roles) {
  setError('')

  try {
    await updateUserRoles(
      roleUser.id,
      roles
    )

    const updatedUsers = await getUsers()
    setUsers(updatedUsers)

    closeRoleForm()
  } catch (roleError) {
    setError(
      roleError.message ||
        'No fue posible actualizar los roles.'
    )
  }
}

function openStatusConfirm(user) {
  closePasswordChange()
  setIsFormOpen(false)
  setSelectedUser(null)
  setRoleUser(null)
  setStatusUser(user)
}

function closeStatusConfirm() {
  setStatusUser(null)
}

async function handleStatusConfirm() {
  setError('')

  try {
    if (statusUser.is_active) {
      await deactivateUser(statusUser.id)
    } else {
      await activateUser(statusUser.id)
    }

    const updatedUsers = await getUsers()
    setUsers(updatedUsers)

    closeStatusConfirm()
  } catch (statusError) {
    setError(
      statusError.message ||
        'No fue posible actualizar el estado del usuario.'
    )
  }
}

function openPasswordChange() {
  setIsFormOpen(false)
  setSelectedUser(null)
  setRoleUser(null)
  setStatusUser(null)

  setPasswordChangeError('')
  setPasswordChangeSuccess('')
  setIsPasswordChangeOpen(true)
}

function closePasswordChange() {
  setPasswordChangeError('')
  setPasswordChangeSuccess('')
  setIsPasswordChangeOpen(false)
}

async function handlePasswordChangeSubmit(
  passwordData
) {
  setIsChangingPassword(true)
  setPasswordChangeError('')
  setPasswordChangeSuccess('')

  try {
    const response = await changePassword(
      passwordData
    )

    setPasswordChangeSuccess(
      response?.detail ||
        'Contraseña actualizada correctamente.'
    )
    return true
  } catch (passwordError) {
    const validationMessage =
      passwordError.data?.current_password?.[0] ||
      passwordError.data?.new_password?.[0] ||
      passwordError.data?.new_password_confirm?.[0]

    setPasswordChangeError(
      validationMessage ||
        passwordError.message ||
        'No fue posible cambiar la contraseña.'
    )
    return true
  } finally {
    setIsChangingPassword(false)
  }
}

  const navigationItems = [
    {
      id: 'users',
      label: 'Usuarios',
      icon: 'users',
      active: true,
    },
    {
      id: 'create-user',
      label: 'Nuevo usuario',
      icon: 'user-plus',
      secondary: true,
      onClick: openCreateForm,
    },
    {
      id: 'change-password',
      label: 'Cambiar contraseña',
      icon: 'key',
      secondary: true,
      onClick: openPasswordChange,
    },
  ]

  return (
    <AppShell
    title="Gestión de usuarios"
    subtitle="Usuarios, roles y cuentas institucionales"
    user={user}
    roleLabel="Administración"
    navigationItems={navigationItems}
    onChangeSpace={onChangeSpace}
    onLogout={onLogout}
  >
    <main className="users-page">

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
              {users.length} usuarios registrados
            </p>
          </div>
        </div>

        {error && (
          <div
            className="users-empty"
            role="alert"
          >
            {error}
          </div>
        )}

        {isLoading && (
          <div className="users-empty">
            Cargando usuarios...
          </div>
        )}

        {!isLoading && !error && (
          <UserTable
            users={users}
            onEdit={openEditForm}
            onManageRoles={openRoleForm}
            onToggleStatus={openStatusConfirm}
          />
        )}
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
    {isPasswordChangeOpen && (
      <Modal
        title="Cambiar mi contraseña"
        onClose={closePasswordChange}
      >
        <PasswordChangeForm
          onSubmit={handlePasswordChangeSubmit}
          onCancel={closePasswordChange}
          isSubmitting={isChangingPassword}
          error={passwordChangeError}
          success={passwordChangeSuccess}
        />
      </Modal>
    )}
    </main>
    </AppShell>
  )
}

export default UserManagementPage