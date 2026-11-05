import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function PsychologistHomePage({
  user,
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
      user={user}
      onLogout={onLogout}
      onChangeSpace={onChangeSpace}
      studentContext="PSICOLOGO"
      pageEyebrow="Espacio psicológico"
      pageTitle="Mis estudiantes"
      pageDescription={
        'Consulta los estudiantes que tienes asignados '
        + 'en el contexto psicológico.'
      }
    />
  )
}


export default PsychologistHomePage
