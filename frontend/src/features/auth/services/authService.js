import { apiRequest } from '../../../services/apiClient'

export function login(credentials) {
  return apiRequest('/auth/login/', {
    method: 'POST',
    data: credentials,
  })
}

export function getSession() {
  return apiRequest('/auth/session/')
}

export function logout() {
  return apiRequest('/auth/logout/', {
    method: 'POST',
    data: {},
  })
}