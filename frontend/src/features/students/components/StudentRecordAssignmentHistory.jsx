function formatDateTime(value) {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(
    'es-GT',
    {
      dateStyle: 'short',
      timeStyle: 'short',
    }
  ).format(date)
}


function getProfessionalName(professional) {
  const fullName = [
    professional?.first_name,
    professional?.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return (
    fullName
    || professional?.username
    || 'Profesional no disponible'
  )
}


function getAssignedByName(user) {
  const fullName = [
    user?.first_name,
    user?.last_name,
  ]
    .filter(Boolean)
    .join(' ')
    .trim()

  return (
    fullName
    || user?.username
    || 'Usuario no disponible'
  )
}


function StudentRecordAssignmentHistory({
  assignments,
}) {
  if (assignments.length === 0) {
    return (
      <div className="student-record-assignments-empty">
        No existen asignaciones registradas para este
        estudiante.
      </div>
    )
  }

  return (
    <div className="student-record-table-container">
      <table className="student-record-assignments-table">
        <thead>
          <tr>
            <th scope="col">
              Rol
            </th>

            <th scope="col">
              Profesional
            </th>

            <th scope="col">
              Asignado
            </th>

            <th scope="col">
              Finalizado
            </th>

            <th scope="col">
              Estado
            </th>

            <th scope="col">
              Asignado por
            </th>
          </tr>
        </thead>

        <tbody>
          {assignments.map((assignment) => (
            <tr key={assignment.id}>
              <td>
                {assignment.professional_role}
              </td>

              <td>
                {getProfessionalName(
                  assignment.professional
                )}
              </td>

              <td>
                {formatDateTime(
                  assignment.assigned_at
                )}
              </td>

              <td>
                {formatDateTime(
                  assignment.unassigned_at
                )}
              </td>

              <td>
                <span
                  className={
                    assignment.is_active
                      ? 'status status--active'
                      : 'status status--inactive'
                  }
                >
                  {assignment.is_active
                    ? 'Activa'
                    : 'Finalizada'}
                </span>
              </td>

              <td>
                {getAssignedByName(
                  assignment.assigned_by
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default StudentRecordAssignmentHistory
