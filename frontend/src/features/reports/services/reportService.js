import { apiRequest } from '../../../services/apiClient'


function contextQuery(context = '') {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  return params
}


export function getReports({
  context = '',
  studentId = '',
  reportType = '',
  dateFrom = '',
  dateTo = '',
} = {}) {
  const params = contextQuery(context)

  if (studentId) {
    params.set('student', studentId)
  }

  if (reportType) {
    params.set('report_type', reportType)
  }

  if (dateFrom) {
    params.set('date_from', dateFrom)
  }

  if (dateTo) {
    params.set('date_to', dateTo)
  }

  return apiRequest(
    `/reports/?${params.toString()}`
  )
}


export function getReport(
  reportId,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    `/reports/${reportId}/?${params.toString()}`
  )
}


export function createReport(
  reportData,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    `/reports/?${params.toString()}`,
    {
      method: 'POST',
      data: reportData,
    }
  )
}

export function exportReport(
  reportId,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    `/reports/${reportId}/export/?${params.toString()}`,
    {
      responseType: 'blob',
    }
  )
}
