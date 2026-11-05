import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function TherapistHomePage({
  user,
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
      user={user}
      onLogout={onLogout}
      onChangeSpace={onChangeSpace}
      studentContext="TERAPEUTA"
      pageEyebrow="Espacio terapéutico"
      pageTitle="Mis estudiantes"
      pageDescription={
        'Consulta los estudiantes que tienes asignados '
        + 'en el contexto terapéutico.'
      }
    />
  )
}


export default TherapistHomePage
