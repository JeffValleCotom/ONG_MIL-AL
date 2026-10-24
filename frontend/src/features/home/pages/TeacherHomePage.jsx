import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function TeacherHomePage({
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
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
