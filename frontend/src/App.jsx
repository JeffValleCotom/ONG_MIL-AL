import { useState } from 'react'

import LoginPage from './features/auth/pages/LoginPage'
import PasswordResetPage
  from './features/auth/pages/PasswordResetPage'
import { logout } from './features/auth/services/authService'
import StudentManagementPage
  from './features/students/pages/StudentManagementPage'
import UserManagementPage
  from './features/users/pages/UserManagementPage'


const STUDENT_VIEW_ROLES = [
  'DOCENTE',
  'PSICOLOGO',
  'TERAPEUTA',
  'RESPONSABLE_INSTITUCIONAL',
]


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

  const roles = authenticatedUser?.roles ?? []

  const isAdministrator =
    roles.includes('ADMINISTRADOR')

  const canViewStudents =
    STUDENT_VIEW_ROLES.some(
      (role) => roles.includes(role)
    )

  const canManageStudents =
    roles.includes('RESPONSABLE_INSTITUCIONAL')

  if (isAdministrator) {
    return (
      <UserManagementPage
        onLogout={handleManagementLogout}
      />
    )
  }

  if (canViewStudents) {
    return (
      <StudentManagementPage
        onLogout={handleManagementLogout}
        canManageStudents={canManageStudents}
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
