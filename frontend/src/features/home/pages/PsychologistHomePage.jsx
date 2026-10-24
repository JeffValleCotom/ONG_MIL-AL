import StudentManagementPage
  from '../../students/pages/StudentManagementPage'


function PsychologistHomePage({
  onLogout,
  onChangeSpace,
}) {
  return (
    <StudentManagementPage
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
