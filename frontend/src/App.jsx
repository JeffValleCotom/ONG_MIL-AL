import { useState } from 'react'

import LoginPage from './features/auth/pages/LoginPage'
import PasswordResetPage
  from './features/auth/pages/PasswordResetPage'
import { logout } from './features/auth/services/authService'
import InstitutionalHomePage
  from './features/home/pages/InstitutionalHomePage'
import PsychologistHomePage
  from './features/home/pages/PsychologistHomePage'
import RoleSpaceSelectorPage
  from './features/home/pages/RoleSpaceSelectorPage'
import TeacherHomePage
  from './features/home/pages/TeacherHomePage'
import TherapistHomePage
  from './features/home/pages/TherapistHomePage'
import UserManagementPage
  from './features/users/pages/UserManagementPage'


const SPACE_DEFINITIONS = [
  {
    role: 'ADMINISTRADOR',
    label: 'Administración',
    description:
      'Gestión de usuarios, roles y cuentas institucionales.',
  },
  {
    role: 'RESPONSABLE_INSTITUCIONAL',
    label: 'Gestión institucional',
    description:
      'Gestión general de estudiantes y asignaciones profesionales.',
  },
  {
    role: 'DOCENTE',
    label: 'Espacio docente',
    description:
      'Consulta de estudiantes asignados en el contexto docente.',
  },
  {
    role: 'PSICOLOGO',
    label: 'Espacio psicológico',
    description:
      'Consulta de estudiantes asignados en el contexto psicológico.',
  },
  {
    role: 'TERAPEUTA',
    label: 'Espacio terapéutico',
    description:
      'Consulta de estudiantes asignados en el contexto terapéutico.',
  },
]


function App() {
  const [authenticatedUser, setAuthenticatedUser] =
    useState(null)

  const [selectedSpace, setSelectedSpace] =
    useState(null)

  const isPasswordResetPath =
    window.location.pathname === '/password-reset'

  async function handleManagementLogout() {
    await logout()
    setAuthenticatedUser(null)
    setSelectedSpace(null)
  }

  function handleAuthenticated(user) {
    setAuthenticatedUser(user)
    setSelectedSpace(null)
  }

  function handleChangeSpace() {
    setSelectedSpace(null)
  }

  if (isPasswordResetPath) {
    return <PasswordResetPage />
  }

  if (!authenticatedUser) {
    return (
      <LoginPage
        onAuthenticated={handleAuthenticated}
        onLoggedOut={() => {
          setAuthenticatedUser(null)
          setSelectedSpace(null)
        }}
      />
    )
  }

  const roles = authenticatedUser.roles ?? []

  const availableSpaces =
    SPACE_DEFINITIONS.filter(
      (space) => roles.includes(space.role)
    )

  const selectedSpaceIsAvailable =
    availableSpaces.some(
      (space) => space.role === selectedSpace
    )

  const activeSpace =
    availableSpaces.length === 1
      ? availableSpaces[0].role
      : (
          selectedSpaceIsAvailable
            ? selectedSpace
            : null
        )

  if (!activeSpace) {
    return (
      <RoleSpaceSelectorPage
        user={authenticatedUser}
        spaces={availableSpaces}
        onSelect={setSelectedSpace}
        onLogout={handleManagementLogout}
      />
    )
  }

  const onChangeSpace =
    availableSpaces.length > 1
      ? handleChangeSpace
      : undefined

  if (activeSpace === 'ADMINISTRADOR') {
    return (
      <UserManagementPage
        onLogout={handleManagementLogout}
        onChangeSpace={onChangeSpace}
      />
    )
  }

  if (activeSpace === 'RESPONSABLE_INSTITUCIONAL') {
    return (
      <InstitutionalHomePage
        onLogout={handleManagementLogout}
        onChangeSpace={onChangeSpace}
      />
    )
  }

  if (activeSpace === 'DOCENTE') {
    return (
      <TeacherHomePage
        onLogout={handleManagementLogout}
        onChangeSpace={onChangeSpace}
      />
    )
  }

  if (activeSpace === 'PSICOLOGO') {
    return (
      <PsychologistHomePage
        onLogout={handleManagementLogout}
        onChangeSpace={onChangeSpace}
      />
    )
  }

  if (activeSpace === 'TERAPEUTA') {
    return (
      <TherapistHomePage
        onLogout={handleManagementLogout}
        onChangeSpace={onChangeSpace}
      />
    )
  }

  return null
}


export default App
