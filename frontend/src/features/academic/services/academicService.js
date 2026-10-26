import { apiRequest } from '../../../services/apiClient'


function buildContextQuery(context) {
  const params = new URLSearchParams()

  if (context) {
    params.set('context', context)
  }

  return params.toString()
}


export function createAcademicFollowUp({
  studentId,
  context,
  followUpData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/academic-followups/`
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


export function updateAcademicFollowUp({
  followUpId,
  context,
  followUpData,
}) {
  const queryString = buildContextQuery(context)

  return apiRequest(
    `/academic-followups/${followUpId}/`
    + `${queryString ? `?${queryString}` : ''}`,
    {
      method: 'PATCH',
      data: followUpData,
    }
  )
}
