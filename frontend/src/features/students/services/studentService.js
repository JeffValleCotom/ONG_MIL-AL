import { apiRequest } from '../../../services/apiClient'

export function createStudent(studentData) {
  return apiRequest('/students/', {
    method: 'POST',
    data: studentData,
  })
}