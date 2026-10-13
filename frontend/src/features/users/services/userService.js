import { apiRequest } from '../../../services/apiClient'

export function getUsers() {
  return apiRequest('/users/')
}

export function createUser(userData) {
  return apiRequest('/users/', {
    method: 'POST',
    data: userData,
  })
}

export function updateUser(userId, userData) {
  return apiRequest(`/users/${userId}/`, {
    method: 'PATCH',
    data: userData,
  })
}

export function getUserRoles(userId) {
  return apiRequest(`/users/${userId}/roles/`)
}

export function updateUserRoles(userId, roles) {
  return apiRequest(`/users/${userId}/roles/`, {
    method: 'PATCH',
    data: {
      roles,
    },
  })
}

export function activateUser(userId) {
  return apiRequest(`/users/${userId}/activate/`, {
    method: 'PATCH',
    data: {},
  })
}

export function deactivateUser(userId) {
  return apiRequest(`/users/${userId}/deactivate/`, {
    method: 'PATCH',
    data: {},
  })
}