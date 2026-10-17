function formatDate(value) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}/${month}/${year}`
}


function StudentTable({
  students,
}) {
  if (students.length === 0) {
    return (
      <div className="students-empty">
        No se encontraron estudiantes.
      </div>
    )
  }

  return (
    <div className="table-container">
      <table className="students-table">
        <thead>
          <tr>
            <th scope="col">
              Código
            </th>

            <th scope="col">
              Estudiante
            </th>

            <th scope="col">
              Fecha de nacimiento
            </th>

            <th scope="col">
              Fecha de ingreso
            </th>

            <th scope="col">
              Estado
            </th>
          </tr>
        </thead>

        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>
                <strong>
                  {student.institutional_code}
                </strong>
              </td>

              <td>
                <div className="student-identity">
                  <strong>
                    {student.first_name}
                    {' '}
                    {student.last_name}
                  </strong>
                </div>
              </td>

              <td>
                {formatDate(
                  student.date_of_birth
                )}
              </td>

              <td>
                {formatDate(
                  student.admission_date
                )}
              </td>

              <td>
                <span
                  className={
                    student.is_active
                      ? 'status status--active'
                      : 'status status--inactive'
                  }
                >
                  {student.is_active
                    ? 'Activo'
                    : 'Inactivo'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default StudentTable
