import { useState } from 'react'

import LoginPage from './features/auth/pages/LoginPage'
import PasswordResetPage
  from './features/auth/pages/PasswordResetPage'
import { logout } from './features/auth/services/authService'
import StudentManagementPage
  from './features/students/pages/StudentManagementPage'
import UserManagementPage
  from './features/users/pages/UserManagementPage'


function App() {
  const [authenticatedUser, setAuthenticatedUser] =
    useState(null)

  const isPasswordResetPath =
    window.location.pathname === '/password-reset'

  async function handleManagementLogout() {
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

  const isInstitutionalResponsible =
    authenticatedUser?.roles?.includes(
      'RESPONSABLE_INSTITUCIONAL'
    )

  if (isAdministrator) {
    return (
      <UserManagementPage
        onLogout={handleManagementLogout}
      />
    )
  }

  if (isInstitutionalResponsible) {
    return (
      <StudentManagementPage
        onLogout={handleManagementLogout}
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
