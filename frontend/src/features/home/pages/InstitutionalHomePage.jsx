import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function InstitutionalHomePage({
  user,
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
      user={user}
      onLogout={onLogout}
      onChangeSpace={onChangeSpace}
      canManageStudents
      studentContext="RESPONSABLE_INSTITUCIONAL"
      pageEyebrow="Gestión institucional"
      pageTitle="Estudiantes de MIL-AL"
      pageDescription={
        'Administra la información general de los '
        + 'estudiantes y sus asignaciones profesionales.'
      }
    />
  )
}


export default InstitutionalHomePage
