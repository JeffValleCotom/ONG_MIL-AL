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

export function changePassword(passwordData) {
  return apiRequest('/auth/password/change/', {
    method: 'POST',
    data: passwordData,
  })
}

export function requestPasswordRecovery(email) {
  return apiRequest(
    '/auth/password/recovery/request/',
    {
      method: 'POST',
      data: {
        email,
      },
    }
  )
}

export function verifyPasswordRecovery(
  uid,
  token
) {
  return apiRequest(
    '/auth/password/recovery/verify/',
    {
      method: 'POST',
      data: {
        uid,
        token,
      },
    }
  )
}

export function confirmPasswordRecovery({
  uid,
  token,
  newPassword,
  newPasswordConfirm,
}) {
  return apiRequest(
    '/auth/password/recovery/confirm/',
    {
      method: 'POST',
      data: {
        uid,
        token,
        new_password: newPassword,
        new_password_confirm:
          newPasswordConfirm,
      },
    }
  )
}
