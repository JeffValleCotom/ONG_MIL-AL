import { useState } from 'react'

import LoginPage from './features/auth/pages/LoginPage'
import UserManagementPage from './features/users/pages/UserManagementPage'
import { logout } from './features/auth/services/authService'
import PasswordResetPage
  from './features/auth/pages/PasswordResetPage'


function App() {
  const [authenticatedUser, setAuthenticatedUser] =
    useState(null)

  const isPasswordResetPath =
  window.location.pathname === '/password-reset'

  async function handleAdministratorLogout() {
    await logout()
    setAuthenticatedUser(null)
  }

  if (isPasswordResetPath) {
  return <PasswordResetPage />
  }

  const isAdministrator =
    authenticatedUser?.roles?.includes(
      'ADMINISTRADOR'
    )

  if (isAdministrator) {
    return (
      <UserManagementPage
        onLogout={handleAdministratorLogout}
      />
    )
  }

  return (
    <LoginPage
      onAuthenticated={setAuthenticatedUser}
      onLoggedOut={() => setAuthenticatedUser(null)}
    />
  )
}

export default App