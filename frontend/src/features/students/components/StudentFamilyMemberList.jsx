const RELATIONSHIP_LABELS = {
  MADRE: 'Madre',
  PADRE: 'Padre',
  HERMANO_A: 'Hermano/a',
  ABUELO_A: 'Abuelo/a',
  TIO_A: 'Tío/a',
  TUTOR: 'Tutor',
  CUIDADOR: 'Cuidador',
  OTRO: 'Otro',
}

function getRelationshipLabel(member) {
  if (member.relationship === 'OTRO') {
    return member.relationship_detail
      ? `Otro — ${member.relationship_detail}`
      : 'Otro'
  }

  return (
    RELATIONSHIP_LABELS[member.relationship]
    ?? member.relationship
  )
}

function displayValue(value) {
  return value || '—'
}

function StudentFamilyMemberList({
  familyMembers = [],
}) {
  if (familyMembers.length === 0) {
    return (
      <div className="student-family-empty">
        <p>
          No hay información familiar registrada para este
          estudiante.
        </p>
      </div>
    )
  }

  return (
    <div className="student-family-list">
      {familyMembers.map((member) => (
        <article
          className={
            'student-family-member'
            + (
              member.is_active
                ? ''
                : ' student-family-member--inactive'
            )
          }
          key={member.id}
        >
          <div className="student-family-member__header">
            <div>
              <h3>
                {member.first_name} {member.last_name}
              </h3>

              <p>
                {getRelationshipLabel(member)}
              </p>
            </div>

            <div className="student-family-member__badges">
              {member.is_primary_contact && (
                <span
                  className={
                    'student-family-badge '
                    + 'student-family-badge--primary'
                  }
                >
                  Contacto principal
                </span>
              )}

              <span
                className={
                  'student-family-badge '
                  + (
                    member.is_active
                      ? 'student-family-badge--active'
                      : 'student-family-badge--inactive'
                  )
                }
              >
                {member.is_active
                  ? 'Activo'
                  : 'Histórico'}
              </span>
            </div>
          </div>

          <dl className="student-family-member__details">
            <div>
              <dt>Teléfono</dt>
              <dd>{displayValue(member.phone)}</dd>
            </div>

            <div>
              <dt>Correo</dt>
              <dd>{displayValue(member.email)}</dd>
            </div>

            <div>
              <dt>Dirección</dt>
              <dd>{displayValue(member.address)}</dd>
            </div>
          </dl>
        </article>
      ))}
    </div>
  )
}

export default StudentFamilyMemberList
