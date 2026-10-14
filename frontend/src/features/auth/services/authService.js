import { apiRequest } from '../../../services/apiClient'

export async function getCsrfToken() {
  const response = await apiRequest('/auth/csrf/')

  return response.csrfToken
}

export async function login(credentials) {
  const csrfToken = await getCsrfToken()

  return apiRequest('/auth/login/', {
    method: 'POST',
    data: credentials,
    headers: {
      'X-CSRFToken': csrfToken,
    },
  })
}

export async function getSession() {
  return apiRequest('/auth/session/')
}