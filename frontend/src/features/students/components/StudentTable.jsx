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
  canManageStudents = false,
  onViewRecord,
  onEdit,
  onToggleStatus,
  onManageAssignments,
}) {
  if (students.length === 0) {
    return (
      <div className="students-empty">
        No se encontraron estudiantes.
      </div>
    )
  }

  const hasActions =
    Boolean(onViewRecord)
    || canManageStudents

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

            {hasActions && (
              <th scope="col">
                Acciones
              </th>
            )}
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

              {hasActions && (
                <td>
                  <div className="student-actions">
                    {onViewRecord && (
                      <button
                        className="button button--primary"
                        type="button"
                        onClick={() => {
                          onViewRecord(student)
                        }}
                      >
                        Expediente
                      </button>
                    )}

                    {canManageStudents && (
                      <>
                        <button
                          className="button button--secondary"
                          type="button"
                          onClick={() => {
                            onManageAssignments?.(student)
                          }}
                        >
                          Asignaciones
                        </button>

                        <button
                          className="button button--secondary"
                          type="button"
                          onClick={() => {
                            onEdit?.(student)
                          }}
                        >
                          Editar
                        </button>

                        <button
                          className={
                            student.is_active
                              ? 'button button--danger'
                              : 'button button--primary'
                          }
                          type="button"
                          onClick={() => {
                            onToggleStatus?.(student)
                          }}
                        >
                          {student.is_active
                            ? 'Desactivar'
                            : 'Activar'}
                        </button>
                      </>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default StudentTable
