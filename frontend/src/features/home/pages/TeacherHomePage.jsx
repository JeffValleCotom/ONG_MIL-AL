import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function TeacherHomePage({
  user,
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
      user={user}
      onLogout={onLogout}
      onChangeSpace={onChangeSpace}
      studentContext="DOCENTE"
      pageEyebrow="Espacio docente"
      pageTitle="Mis estudiantes"
      pageDescription={
        'Consulta los estudiantes que tienes asignados '
        + 'en el contexto docente.'
      }
    />
  )
}


export default TeacherHomePage
