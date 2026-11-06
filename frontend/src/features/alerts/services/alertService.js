import { apiRequest } from '../../../services/apiClient'


function buildAlertParams({
  context = '',
  status = '',
} = {}) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  if (status) {
    params.set('status', status)
  }

  return params.toString()
}


export function getAlerts({
  context = '',
  status = '',
} = {}) {
  const queryString = buildAlertParams({
    context,
    status,
  })

  return apiRequest(
    `/alerts/${queryString
      ? `?${queryString}`
      : ''}`
  )
}


export function getAlertSummary(
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/alerts/summary/${queryString
      ? `?${queryString}`
      : ''}`
  )
}


export function reviewAlert(
  alertId,
  context = ''
) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  const queryString = params.toString()

  return apiRequest(
    `/alerts/${alertId}/review/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: {},
    }
  )
}
