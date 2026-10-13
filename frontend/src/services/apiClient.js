const API_BASE_URL = '/api/v1'

export async function apiRequest(
  path,
  {
    method = 'GET',
    data,
    headers = {},
    ...options
  } = {}
) {
  const requestOptions = {
    ...options,
    method,
    credentials: 'same-origin',
    headers: {
      ...headers,
    },
  }

  if (data !== undefined) {
    requestOptions.headers['Content-Type'] = 'application/json'
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