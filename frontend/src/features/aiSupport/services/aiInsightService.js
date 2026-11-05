import { apiRequest } from '../../../services/apiClient'


function contextQuery(context = '') {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  return params
}


export function getAIInsights({
  context = '',
  studentId = '',
  sourceReportId = '',
  kind = '',
  reviewStatus = '',
  dateFrom = '',
  dateTo = '',
} = {}) {
  const params = contextQuery(context)

  if (studentId) {
    params.set('student', studentId)
  }

  if (sourceReportId) {
    params.set(
      'source_report',
      sourceReportId
    )
  }

  if (kind) {
    params.set('kind', kind)
  }

  if (reviewStatus) {
    params.set(
      'review_status',
      reviewStatus
    )
  }

  if (dateFrom) {
    params.set('date_from', dateFrom)
  }

  if (dateTo) {
    params.set('date_to', dateTo)
  }

  return apiRequest(
    `/ai-insights/?${params.toString()}`
  )
}


export function getAIInsight(
  insightId,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    `/ai-insights/${insightId}/?${params.toString()}`
  )
}


export function createAIInsight(
  insightData,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    `/ai-insights/?${params.toString()}`,
    {
      method: 'POST',
      data: insightData,
    }
  )
}


export function reviewAIInsight(
  insightId,
  reviewData,
  context
) {
  const params = contextQuery(context)

  return apiRequest(
    (
      `/ai-insights/${insightId}/review/`
      + `?${params.toString()}`
    ),
    {
      method: 'PATCH',
      data: reviewData,
    }
  )
}
