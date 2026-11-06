import { apiRequest } from '../../../services/apiClient'


export function getDashboardOverview({
  context = '',
  dateFrom = '',
  dateTo = '',
} = {}) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  if (dateFrom) {
    params.set('date_from', dateFrom)
  }

  if (dateTo) {
    params.set('date_to', dateTo)
  }

  const queryString = params.toString()

  return apiRequest(
    `/dashboard/overview/${queryString
      ? `?${queryString}`
      : ''}`
  )
}
