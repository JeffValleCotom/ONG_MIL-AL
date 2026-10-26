import { apiRequest } from '../../../services/apiClient'


function buildContextQuery(context) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  return params.toString()
}


export function createPsychologicalFollowUp({
  studentId,
  context,
  followUpData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/psychological-followups/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'POST',
      data: {
        student_id: studentId,
        ...followUpData,
      },
    }
  )
}


export function updatePsychologicalFollowUp({
  followUpId,
  context,
  followUpData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/psychological-followups/${followUpId}/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: followUpData,
    }
  )
}
