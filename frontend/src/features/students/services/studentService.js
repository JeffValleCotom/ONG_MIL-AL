import { apiRequest } from '../../../services/apiClient'


export function getStudents({
  search = '',
  status = '',
} = {}) {
  const params = new URLSearchParams()

  const normalizedSearch = search.trim()

  if (normalizedSearch) {
    params.set('search', normalizedSearch)
  }

  if (status) {
    params.set('status', status)
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
