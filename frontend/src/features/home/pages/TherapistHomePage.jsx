import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function TherapistHomePage({
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
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
