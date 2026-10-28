import { apiRequest } from '../../../services/apiClient'


export function getStudents({
  search = '',
  status = '',
  context = '',
} = {}) {
  const params = new URLSearchParams()

  const normalizedSearch = search.trim()

  if (normalizedSearch) {
    params.set('search', normalizedSearch)
  }

  if (status) {
    params.set('status', status)
  }

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/students/${queryString
      ? `?${queryString}`
      : ''}`
  )
}

export function getStudent(studentId) {
  return apiRequest(`/students/${studentId}/`)
}

export function getStudentRecord(
  studentId,
  context
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/students/${studentId}/record/`
    + `${queryString ? `?${queryString}` : ''}`
  )
}

export function createStudent(studentData) {
  return apiRequest('/students/', {
    method: 'POST',
    data: studentData,
  })
}

export function updateStudent(studentId, studentData) {
  return apiRequest(`/students/${studentId}/`, {
    method: 'PATCH',
    data: studentData,
  })
}


export function createStudentFamilyMember(
  studentId,
  familyMemberData,
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/students/${studentId}/family-members/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'POST',
      data: familyMemberData,
    }
  )
}


export function updateStudentFamilyMember(
  studentId,
  familyMemberId,
  familyMemberData,
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/students/${studentId}/family-members/${familyMemberId}/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: familyMemberData,
    }
  )
}


export function deactivateStudentFamilyMember(
  studentId,
  familyMemberId,
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/students/${studentId}/family-members/`
    + `${familyMemberId}/deactivate/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: {},
    }
  )
}


export function activateStudent(studentId) {
  return apiRequest(`/students/${studentId}/activate/`, {
    method: 'PATCH',
    data: {},
  })
}


export function deactivateStudent(studentId) {
  return apiRequest(`/students/${studentId}/deactivate/`, {
    method: 'PATCH',
    data: {},
  })
}

export function getStudentAssignments({
  studentId,
  status = '',
  professionalRole = '',
} = {}) {
  const params = new URLSearchParams()

  if (studentId) {
    params.set('student', studentId)
  }

  if (status) {
    params.set('status', status)
  }

  if (professionalRole) {
    params.set(
      'professional_role',
      professionalRole
    )
  }

  const queryString = params.toString()

  return apiRequest(
    `/student-assignments/${queryString
      ? `?${queryString}`
      : ''}`
  )
}


export function getEligibleProfessionals(role) {
  const params = new URLSearchParams({
    role,
  })

  return apiRequest(
    `/student-assignments/eligible-professionals/`
    + `?${params.toString()}`
  )
}


export function createStudentAssignment({
  studentId,
  professionalId,
  professionalRole,
}) {
  return apiRequest('/student-assignments/', {
    method: 'POST',
    data: {
      student_id: studentId,
      professional_id: professionalId,
      professional_role: professionalRole,
    },
  })
}


export function finishStudentAssignment(
  assignmentId
) {
  return apiRequest(
    `/student-assignments/${assignmentId}/finish/`,
    {
      method: 'PATCH',
      data: {},
    }
  )
}

export function uploadStudentDocument(
  studentId,
  documentData,
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  const formData = new FormData()

  formData.append(
    'document_type',
    documentData.documentType
  )

  if (documentData.documentTypeDetail) {
    formData.append(
      'document_type_detail',
      documentData.documentTypeDetail
    )
  }

  if (documentData.description) {
    formData.append(
      'description',
      documentData.description
    )
  }

  formData.append(
    'file',
    documentData.file
  )

  return apiRequest(
    `/students/${studentId}/documents/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'POST',
      body: formData,
    }
  )
}
