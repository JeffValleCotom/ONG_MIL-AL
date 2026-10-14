import { useState } from 'react'

import LoginPage from './features/auth/pages/LoginPage'
import UserManagementPage from './features/users/pages/UserManagementPage'
import { logout } from './features/auth/services/authService'


function App() {
  const [authenticatedUser, setAuthenticatedUser] =
    useState(null)

  async function handleAdministratorLogout() {
    await logout()
    setAuthenticatedUser(null)
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