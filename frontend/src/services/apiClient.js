const API_BASE_URL = '/api/v1'

const SAFE_METHODS = new Set([
  'GET',
  'HEAD',
  'OPTIONS',
])

async function requestCsrfToken() {
  const response = await fetch(
    `${API_BASE_URL}/auth/csrf/`,
    {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
      },
    }
  )

  if (!response.ok) {
    throw new Error(
      'No fue posible obtener el token de seguridad.'
    )
  }

  const data = await response.json()

  if (!data?.csrfToken) {
    throw new Error(
      'El servidor no proporcionó un token de seguridad.'
    )
  }

  return data.csrfToken
}

export async function apiRequest(
  path,
  {
    method = 'GET',
    data,
    headers = {},
    ...options
  } = {}
) {
  const normalizedMethod = method.toUpperCase()
  const requestHeaders = new Headers(headers)

  if (
    !SAFE_METHODS.has(normalizedMethod) &&
    !requestHeaders.has('X-CSRFToken')
  ) {
    const csrfToken = await requestCsrfToken()

    requestHeaders.set(
      'X-CSRFToken',
      csrfToken
    )
  }

  const requestOptions = {
    ...options,
    method: normalizedMethod,
    credentials: 'same-origin',
    headers: requestHeaders,
  }

  if (data !== undefined) {
    requestHeaders.set(
      'Content-Type',
      'application/json'
    )

    requestOptions.body = JSON.stringify(data)
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    requestOptions
  )

  let responseData

  try {
    responseData = await response.json()
  } catch {
    responseData = null
  }

  if (!response.ok) {
    const error = new Error(
      responseData?.detail ||
        'No fue posible completar la solicitud.'
    )

    error.status = response.status
    error.data = responseData

    throw error
  }

  return responseData
}