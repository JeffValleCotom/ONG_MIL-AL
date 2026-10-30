import { apiRequest } from '../../../services/apiClient'


function buildContextQuery(context) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  return params.toString()
}


export function createEvaluation({
  studentId,
  context,
  evaluationData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/evaluations/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'POST',
      data: {
        student_id: studentId,
        ...evaluationData,
      },
    }
  )
}


export function updateEvaluation({
  evaluationId,
  context,
  evaluationData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/evaluations/${evaluationId}/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: evaluationData,
    }
  )
}
