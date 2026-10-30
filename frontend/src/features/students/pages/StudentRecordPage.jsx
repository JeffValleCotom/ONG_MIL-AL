import { useEffect, useState } from 'react'

import AcademicFollowUpForm
  from '../../academic/components/AcademicFollowUpForm'
import AcademicFollowUpList
  from '../../academic/components/AcademicFollowUpList'
import {
  createAcademicFollowUp,
  updateAcademicFollowUp,
} from '../../academic/services/academicService'
import {
  createStudentFamilyMember,
  updateStudentFamilyMember,
  deactivateStudentFamilyMember,
  getStudentRecord,
  updateStudent,
  uploadStudentDocument,
  downloadStudentDocument,
  getStudentDocuments,
} from '../services/studentService'
import StudentEditForm
  from '../components/StudentEditForm'
import StudentFamilyMemberForm
  from '../components/StudentFamilyMemberForm'
import StudentFamilyMemberList
  from '../components/StudentFamilyMemberList'
import './StudentRecordPage.css'
import PsychologicalFollowUpForm
  from '../../psychology/components/PsychologicalFollowUpForm'
import PsychologicalFollowUpList
  from '../../psychology/components/PsychologicalFollowUpList'
import {
  createPsychologicalFollowUp,
  updatePsychologicalFollowUp,
} from '../../psychology/services/psychologyService'
import TherapyFollowUpForm
  from '../../therapy/components/TherapyFollowUpForm'
import TherapyFollowUpList
  from '../../therapy/components/TherapyFollowUpList'
import {
  createTherapyFollowUp,
  updateTherapyFollowUp,
} from '../../therapy/services/therapyService'
import StudentRecordAssignmentHistory
  from '../components/StudentRecordAssignmentHistory'
import StudentDocumentUploadForm
  from '../components/StudentDocumentUploadForm'
import StudentDocumentList
  from '../components/StudentDocumentList'
import EvaluationForm
  from '../../evaluations/components/EvaluationForm'
import EvaluationList
  from '../../evaluations/components/EvaluationList'
import {
  createEvaluation,
  updateEvaluation,
} from '../../evaluations/services/evaluationService'


function formatDate(value) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}/${month}/${year}`
}


function getRecordErrorMessage(error) {
  const data = error?.data

  if (data?.context) {
    const value = data.context

    if (Array.isArray(value)) {
      return value[0]
    }

    if (typeof value === 'string') {
      return value
    }
  }

  return (
    data?.detail
    || error?.message
    || 'No fue posible cargar el expediente.'
  )
}


function getAcademicErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible guardar el seguimiento académico.'
    )
  }

  const fieldOrder = [
    'student_id',
    'followup_date',
    'academic_period',
    'subject',
    'observations',
    'strengths',
    'areas_for_improvement',
    'recommendations',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible guardar el seguimiento académico.'
  )
}

function getPsychologicalErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible guardar el seguimiento psicológico.'
    )
  }

  const fieldOrder = [
    'student_id',
    'followup_date',
    'reason',
    'observations',
    'emotional_behavioral_notes',
    'recommendations',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible guardar el seguimiento psicológico.'
  )
}

function getTherapyErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible guardar el seguimiento terapéutico.'
    )
  }

  const fieldOrder = [
    'student_id',
    'followup_date',
    'therapy_area',
    'objectives',
    'activities',
    'progress_notes',
    'recommendations',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible guardar el seguimiento terapéutico.'
  )
}

function getEvaluationErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible guardar la evaluación.'
    )
  }

  const fieldOrder = [
    'student_id',
    'evaluation_date',
    'evaluation_type',
    'results',
    'observations',
    'professional_role',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible guardar la evaluación.'
  )
}

function getFamilyErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible registrar el familiar.'
    )
  }

  const fieldOrder = [
    'first_name',
    'last_name',
    'relationship',
    'relationship_detail',
    'phone',
    'email',
    'address',
    'is_primary_contact',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible registrar el familiar.'
  )
}

function getDocumentErrorMessage(error) {
  const data = error?.data

  if (!data) {
    return (
      error?.message
      || 'No fue posible cargar el documento.'
    )
  }

  const fieldOrder = [
    'file',
    'document_type',
    'document_type_detail',
    'description',
    'context',
    'detail',
  ]

  for (const field of fieldOrder) {
    const value = data[field]

    if (
      Array.isArray(value)
      && value.length > 0
    ) {
      return value[0]
    }

    if (
      typeof value === 'string'
      && value
    ) {
      return value
    }
  }

  return (
    error?.message
    || 'No fue posible cargar el documento.'
  )
}

function StudentRecordPage({
  studentId,
  studentContext,
  onBack,
}) {
  const [record, setRecord] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [
    isGeneralFormOpen,
    setIsGeneralFormOpen,
  ] = useState(false)

  const [
    isSavingGeneral,
    setIsSavingGeneral,
  ] = useState(false)

  const [
    generalError,
    setGeneralError,
  ] = useState('')

  const [
    generalSuccess,
    setGeneralSuccess,
  ] = useState('')

  const [
    isFamilyFormOpen,
    setIsFamilyFormOpen,
  ] = useState(false)

  const [
    editingFamilyMember,
    setEditingFamilyMember,
  ] = useState(null)

  const [
    deactivatingFamilyMemberId,
    setDeactivatingFamilyMemberId,
  ] = useState(null)

  const [
    isSavingFamily,
    setIsSavingFamily,
  ] = useState(false)

  const [
    familyError,
    setFamilyError,
  ] = useState('')

  const [
    familySuccess,
    setFamilySuccess,
  ] = useState('')

  const [
    isAcademicFormOpen,
    setIsAcademicFormOpen,
  ] = useState(false)

  const [
    editingFollowUp,
    setEditingFollowUp,
  ] = useState(null)

  const [
    isSavingAcademic,
    setIsSavingAcademic,
  ] = useState(false)

  const [
    academicError,
    setAcademicError,
  ] = useState('')

  const [
    academicSuccess,
    setAcademicSuccess,
  ] = useState('')

  const [
    isPsychologicalFormOpen,
    setIsPsychologicalFormOpen,
  ] = useState(false)

  const [
    editingPsychologicalFollowUp,
    setEditingPsychologicalFollowUp,
  ] = useState(null)

  const [
    isSavingPsychological,
    setIsSavingPsychological,
  ] = useState(false)

  const [
    psychologicalError,
    setPsychologicalError,
  ] = useState('')

  const [
    psychologicalSuccess,
    setPsychologicalSuccess,
  ] = useState('')

  const [
    isTherapyFormOpen,
    setIsTherapyFormOpen,
  ] = useState(false)

  const [
    isEvaluationFormOpen,
    setIsEvaluationFormOpen,
  ] = useState(false)

  const [
    editingEvaluation,
    setEditingEvaluation,
  ] = useState(null)

  const [
    isSavingEvaluation,
    setIsSavingEvaluation,
  ] = useState(false)

  const [
    evaluationError,
    setEvaluationError,
  ] = useState('')

  const [
    evaluationSuccess,
    setEvaluationSuccess,
  ] = useState('')

  const [
    editingTherapyFollowUp,
    setEditingTherapyFollowUp,
  ] = useState(null)

  const [
    isSavingTherapy,
    setIsSavingTherapy,
  ] = useState(false)

  const [
    therapyError,
    setTherapyError,
  ] = useState('')

  const [
    therapySuccess,
    setTherapySuccess,
  ] = useState('')

  const [
    isDocumentFormOpen,
    setIsDocumentFormOpen,
  ] = useState(false)

  const [
    isSavingDocument,
    setIsSavingDocument,
  ] = useState(false)

  const [
    documentError,
    setDocumentError,
  ] = useState('')

  const [
    documentSuccess,
    setDocumentSuccess,
  ] = useState('')

  const [
    documents,
    setDocuments,
  ] = useState([])

  const [
    isLoadingDocuments,
    setIsLoadingDocuments,
  ] = useState(true)

  const [
    documentQueryError,
    setDocumentQueryError,
  ] = useState('')

  const [
    downloadingDocumentId,
    setDownloadingDocumentId,
  ] = useState(null)

  useEffect(() => {
    let isMounted = true

    async function loadRecord() {
      setIsLoading(true)
      setError('')

      try {
        const data = await getStudentRecord(
          studentId,
          studentContext
        )

        if (isMounted) {
          setRecord(data)
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            getRecordErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadRecord()

    return () => {
      isMounted = false
    }
  }, [studentId, studentContext])

  useEffect(() => {
    let isMounted = true

    async function loadDocuments() {
      setIsLoadingDocuments(true)
      setDocumentQueryError('')

      try {
        const data = await getStudentDocuments(
          studentId,
          studentContext
        )

        if (isMounted) {
          setDocuments(data?.items ?? [])
        }
      } catch (loadError) {
        if (isMounted) {
          setDocuments([])
          setDocumentQueryError(
            getDocumentErrorMessage(loadError)
          )
        }
      } finally {
        if (isMounted) {
          setIsLoadingDocuments(false)
        }
      }
    }

    loadDocuments()

    return () => {
      isMounted = false
    }
  }, [studentId, studentContext])

  async function refreshRecord() {
    const data = await getStudentRecord(
      studentId,
      studentContext
    )

    setRecord(data)
  }

  async function refreshDocuments() {
    const data = await getStudentDocuments(
      studentId,
      studentContext
    )

    setDocuments(data?.items ?? [])
  }

  function handleGeneralEdit() {
    setGeneralError('')
    setGeneralSuccess('')
    setIsGeneralFormOpen(true)
  }


  function handleGeneralCancel() {
    if (isSavingGeneral) {
      return
    }

    setGeneralError('')
    setIsGeneralFormOpen(false)
  }


  async function handleGeneralSubmit(studentData) {
    if (isSavingGeneral) {
      return
    }

    setIsSavingGeneral(true)
    setGeneralError('')
    setGeneralSuccess('')

    try {
      await updateStudent(
        studentId,
        studentData
      )

      setIsGeneralFormOpen(false)
      setGeneralSuccess(
        'Información general actualizada correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setGeneralError(
          'La información fue actualizada, pero no fue '
          + 'posible refrescar el expediente.'
        )
      }
    } catch (saveError) {
      const data = saveError?.data

      const fieldOrder = [
        'institutional_code',
        'first_name',
        'last_name',
        'date_of_birth',
        'admission_date',
        'detail',
      ]

      let message = ''

      for (const field of fieldOrder) {
        const fieldError = data?.[field]

        if (
          Array.isArray(fieldError)
          && fieldError.length > 0
        ) {
          message = fieldError[0]
          break
        }

        if (typeof fieldError === 'string') {
          message = fieldError
          break
        }
      }

      setGeneralError(
        message
        || saveError?.message
        || 'No fue posible actualizar la información general.'
      )
    } finally {
      setIsSavingGeneral(false)
    }
  }

  function handleNewAcademicFollowUp() {
    setEditingFollowUp(null)
    setAcademicError('')
    setAcademicSuccess('')
    setIsAcademicFormOpen(true)
  }

  function handleNewFamilyMember() {
    setFamilyError('')
    setFamilySuccess('')
    setIsFamilyFormOpen(true)
  }

  function handleFamilyCancel() {
    if (isSavingFamily) {
      return
    }

    setFamilyError('')
    setIsFamilyFormOpen(false)
  }

  async function handleFamilySubmit(
    familyMemberData
  ) {
    const isEditing = Boolean(
      editingFamilyMember
    )

    setIsSavingFamily(true)
    setFamilyError('')
    setFamilySuccess('')

    try {
      if (isEditing) {
        await updateStudentFamilyMember(
          studentId,
          editingFamilyMember.id,
          familyMemberData,
          studentContext
        )
      } else {
        await createStudentFamilyMember(
          studentId,
          familyMemberData,
          studentContext
        )
      }

      await refreshRecord()

      setEditingFamilyMember(null)
      setIsFamilyFormOpen(false)

      setFamilySuccess(
        isEditing
          ? 'Información familiar actualizada correctamente.'
          : 'Familiar registrado correctamente.'
      )
    } catch (error) {
      // Conserva aquí el mismo manejo de error
      // que ya utilizabas en este método.
      setFamilyError(
        error.message
        || 'No fue posible guardar la información familiar.'
      )
    } finally {
      setIsSavingFamily(false)
    }
  }

  async function handleFamilyDeactivate(member) {
    const confirmed = window.confirm(
      `¿Deseas desactivar a ${member.first_name} `
      + `${member.last_name}? El registro se conservará `
      + 'como información histórica.'
    )

    if (!confirmed) {
      return
    }

    setDeactivatingFamilyMemberId(member.id)
    setFamilyError('')
    setFamilySuccess('')

    try {
      await deactivateStudentFamilyMember(
        studentId,
        member.id,
        studentContext
      )

      await refreshRecord()

      if (
        editingFamilyMember?.id === member.id
      ) {
        setEditingFamilyMember(null)
        setIsFamilyFormOpen(false)
      }

      setFamilySuccess(
        'Familiar desactivado correctamente.'
      )
    } catch (error) {
      setFamilyError(
        error.message
        || 'No fue posible desactivar al familiar.'
      )
    } finally {
      setDeactivatingFamilyMemberId(null)
    }
  }

  function handleOpenFamilyRegistration() {
    setEditingFamilyMember(null)
    setFamilyError('')
    setFamilySuccess('')
    setIsFamilyFormOpen(true)
  }

  function handleFamilyEdit(member) {
    setEditingFamilyMember(member)
    setFamilyError('')
    setFamilySuccess('')
    setIsFamilyFormOpen(true)
  }

  function handleFamilyCancel() {
    setEditingFamilyMember(null)
    setFamilyError('')
    setIsFamilyFormOpen(false)
  }

  function handleAcademicEdit(followUp) {
    setEditingFollowUp(followUp)
    setAcademicError('')
    setAcademicSuccess('')
    setIsAcademicFormOpen(true)
  }

  function handleAcademicCancel() {
    if (isSavingAcademic) {
      return
    }

    setEditingFollowUp(null)
    setAcademicError('')
    setIsAcademicFormOpen(false)
  }

  async function handleAcademicSubmit(
    followUpData
  ) {
    if (isSavingAcademic) {
      return
    }

    const isEditing = Boolean(editingFollowUp)

    setIsSavingAcademic(true)
    setAcademicError('')
    setAcademicSuccess('')

    try {
      if (isEditing) {
        await updateAcademicFollowUp({
          followUpId: editingFollowUp.id,
          context: studentContext,
          followUpData,
        })
      } else {
        await createAcademicFollowUp({
          studentId,
          context: studentContext,
          followUpData,
        })
      }

      setEditingFollowUp(null)
      setIsAcademicFormOpen(false)

      setAcademicSuccess(
        isEditing
          ? 'Seguimiento académico actualizado correctamente.'
          : 'Seguimiento académico registrado correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setAcademicError(
          'El seguimiento fue guardado, pero no fue '
          + 'posible actualizar la vista del expediente.'
        )
      }
    } catch (saveError) {
      setAcademicError(
        getAcademicErrorMessage(saveError)
      )
    } finally {
      setIsSavingAcademic(false)
    }
  }

  function handleNewPsychologicalFollowUp() {
    setEditingPsychologicalFollowUp(null)
    setPsychologicalError('')
    setPsychologicalSuccess('')
    setIsPsychologicalFormOpen(true)
  }

  function handlePsychologicalEdit(followUp) {
    setEditingPsychologicalFollowUp(followUp)
    setPsychologicalError('')
    setPsychologicalSuccess('')
    setIsPsychologicalFormOpen(true)
  }

  function handlePsychologicalCancel() {
    if (isSavingPsychological) {
      return
    }

    setEditingPsychologicalFollowUp(null)
    setPsychologicalError('')
    setIsPsychologicalFormOpen(false)
  }

  async function handlePsychologicalSubmit(
    followUpData
  ) {
    if (isSavingPsychological) {
      return
    }

    const isEditing = Boolean(
      editingPsychologicalFollowUp
    )

    setIsSavingPsychological(true)
    setPsychologicalError('')
    setPsychologicalSuccess('')

    try {
      if (isEditing) {
        await updatePsychologicalFollowUp({
          followUpId:
            editingPsychologicalFollowUp.id,
          context: studentContext,
          followUpData,
        })
      } else {
        await createPsychologicalFollowUp({
          studentId,
          context: studentContext,
          followUpData,
        })
      }

      setEditingPsychologicalFollowUp(null)
      setIsPsychologicalFormOpen(false)

      setPsychologicalSuccess(
        isEditing
          ? 'Seguimiento psicológico actualizado correctamente.'
          : 'Seguimiento psicológico registrado correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setPsychologicalError(
          'El seguimiento fue guardado, pero no fue '
          + 'posible actualizar la vista del expediente.'
        )
      }
    } catch (saveError) {
      setPsychologicalError(
        getPsychologicalErrorMessage(saveError)
      )
    } finally {
      setIsSavingPsychological(false)
    }
  }

  function handleNewTherapyFollowUp() {
    setEditingTherapyFollowUp(null)
    setTherapyError('')
    setTherapySuccess('')
    setIsTherapyFormOpen(true)
  }

  function handleTherapyEdit(followUp) {
    setEditingTherapyFollowUp(followUp)
    setTherapyError('')
    setTherapySuccess('')
    setIsTherapyFormOpen(true)
  }

  function handleTherapyCancel() {
    if (isSavingTherapy) {
      return
    }

    setEditingTherapyFollowUp(null)
    setTherapyError('')
    setIsTherapyFormOpen(false)
  }

  async function handleTherapySubmit(
    followUpData
  ) {
    if (isSavingTherapy) {
      return
    }

    const isEditing = Boolean(
      editingTherapyFollowUp
    )

    setIsSavingTherapy(true)
    setTherapyError('')
    setTherapySuccess('')

    try {
      if (isEditing) {
        await updateTherapyFollowUp({
          followUpId:
            editingTherapyFollowUp.id,
          context: studentContext,
          followUpData,
        })
      } else {
        await createTherapyFollowUp({
          studentId,
          context: studentContext,
          followUpData,
        })
      }

      setEditingTherapyFollowUp(null)
      setIsTherapyFormOpen(false)

      setTherapySuccess(
        isEditing
          ? 'Seguimiento terapéutico actualizado correctamente.'
          : 'Seguimiento terapéutico registrado correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setTherapyError(
          'El seguimiento fue guardado, pero no fue '
          + 'posible actualizar la vista del expediente.'
        )
      }
    } catch (saveError) {
      setTherapyError(
        getTherapyErrorMessage(saveError)
      )
    } finally {
      setIsSavingTherapy(false)
    }
  }

  function handleNewEvaluation() {
    setEditingEvaluation(null)
    setEvaluationError('')
    setEvaluationSuccess('')
    setIsEvaluationFormOpen(true)
  }

  function handleEvaluationEdit(evaluation) {
    setEditingEvaluation(evaluation)
    setEvaluationError('')
    setEvaluationSuccess('')
    setIsEvaluationFormOpen(true)
  }

  function handleEvaluationCancel() {
    if (isSavingEvaluation) {
      return
    }

    setEditingEvaluation(null)
    setEvaluationError('')
    setIsEvaluationFormOpen(false)
  }

  async function handleEvaluationSubmit(
    evaluationData
  ) {
    if (isSavingEvaluation) {
      return
    }

    const isEditing = Boolean(
      editingEvaluation
    )

    setIsSavingEvaluation(true)
    setEvaluationError('')
    setEvaluationSuccess('')

    try {
      if (isEditing) {
        await updateEvaluation({
          evaluationId: editingEvaluation.id,
          context: studentContext,
          evaluationData,
        })
      } else {
        await createEvaluation({
          studentId,
          context: studentContext,
          evaluationData,
        })
      }

      setEditingEvaluation(null)
      setIsEvaluationFormOpen(false)

      setEvaluationSuccess(
        isEditing
          ? 'Evaluación actualizada correctamente.'
          : 'Evaluación registrada correctamente.'
      )

      try {
        await refreshRecord()
      } catch {
        setEvaluationError(
          'La evaluación fue guardada, pero no fue '
          + 'posible actualizar la vista del expediente.'
        )
      }
    } catch (saveError) {
      setEvaluationError(
        getEvaluationErrorMessage(saveError)
      )
    } finally {
      setIsSavingEvaluation(false)
    }
  }

  function handleOpenDocumentUpload() {
    setDocumentError('')
    setDocumentSuccess('')
    setIsDocumentFormOpen(true)
  }

  function handleDocumentCancel() {
    if (isSavingDocument) {
      return
    }

    setDocumentError('')
    setIsDocumentFormOpen(false)
  }

  async function handleDocumentSubmit(
    documentData
  ) {
    if (isSavingDocument) {
      return
    }

    setIsSavingDocument(true)
    setDocumentError('')
    setDocumentSuccess('')

    try {
      await uploadStudentDocument(
        studentId,
        documentData,
        studentContext
      )

      setIsDocumentFormOpen(false)
      setDocumentSuccess(
        'Documento cargado correctamente.'
      )

      try {
        await refreshDocuments()
      } catch {
        setDocumentQueryError(
          'El documento fue cargado, pero no fue '
          + 'posible actualizar el listado.'
        )
      }

    } catch (saveError) {
      setDocumentError(
        getDocumentErrorMessage(saveError)
      )
    } finally {
      setIsSavingDocument(false)
    }
  }

  async function handleDocumentDownload(
    documentItem
  ) {
    if (downloadingDocumentId !== null) {
      return
    }

    setDownloadingDocumentId(
      documentItem.id
    )
    setDocumentQueryError('')

    try {
      const blob = await downloadStudentDocument(
        studentId,
        documentItem.id,
        studentContext
      )

      const objectUrl = URL.createObjectURL(blob)

      const link = window.document.createElement(
        'a'
      )

      link.href = objectUrl
      link.download = documentItem.original_filename
      link.style.display = 'none'

      window.document.body.appendChild(link)
      link.click()
      link.remove()

      window.setTimeout(() => {
        URL.revokeObjectURL(objectUrl)
      }, 0)
    } catch (downloadError) {
      setDocumentQueryError(
        getDocumentErrorMessage(
          downloadError
        )
      )
    } finally {
      setDownloadingDocumentId(null)
    }
  }

  const capabilities = record?.capabilities ?? {}

  const canUpdateGeneral = Boolean(
    capabilities.update_general
  )
  const canManageFamily = Boolean(
    capabilities.manage_family
  )
  const canManageAcademic = Boolean(
    capabilities.manage_academic
  )
  const canManagePsychological = Boolean(
    capabilities.manage_psychological
  )
  const canManageTherapy = Boolean(
    capabilities.manage_therapy
  )
  const canManageEvaluations = Boolean(
    capabilities.manage_evaluations
  )
  const general = record?.sections?.general
  const family = record?.sections?.family
  const assignments =
    record?.sections?.assignments
  const academic = record?.sections?.academic
  const psychological =
    record?.sections?.psychological
  const therapy =
    record?.sections?.therapy
  const evaluationSection =
    record?.sections?.evaluations

  const assignmentItems =
    assignments?.items ?? []
  const familyItems =
    family?.items ?? []

  const academicFollowUps =
    academic?.followups ?? []
  const psychologicalFollowUps =
    psychological?.followups ?? []
  const therapyFollowUps =
    therapy?.followups ?? []
  const evaluationItems =
    evaluationSection?.items ?? []

  return (
    <main className="student-record-page">
      <header className="student-record-page__header">
        <div>
          <p className="student-record-page__eyebrow">
            Expediente individual
          </p>

          <h1>
            {general
              ? `${general.first_name} ${general.last_name}`
              : 'Expediente del estudiante'}
          </h1>

          {record && (
            <p className="student-record-page__description">
              Contexto de consulta: {record.context}
            </p>
          )}
        </div>

        <button
          className="button button--secondary"
          type="button"
          onClick={onBack}
          disabled={
            isSavingGeneral
            || isSavingFamily
            || isSavingAcademic
            || isSavingPsychological
            || isSavingTherapy
            || isSavingDocument
          }
        >
          Volver a estudiantes
        </button>
      </header>

      {isLoading && (
        <section className="student-record-card">
          <div className="student-record-message">
            Cargando expediente...
          </div>
        </section>
      )}

      {!isLoading && error && (
        <section className="student-record-card">
          <div
            className={
              'student-record-message '
              + 'student-record-message--error'
            }
            role="alert"
          >
            {error}
          </div>
        </section>
      )}

      {!isLoading && !error && general && (
        <>
          <section
            className="student-record-card"
            aria-labelledby="general-section-title"
          >
          <div
            className={
              'student-record-card__header '
              + 'student-record-card__header--actions'
            }
          >
            <div>
              <h2 id="general-section-title">
                Información general
              </h2>

              <p>
                Datos institucionales base del estudiante.
              </p>
            </div>

            {canUpdateGeneral
              && !isGeneralFormOpen && (
              <button
                className="button button--primary"
                type="button"
                onClick={handleGeneralEdit}
              >
                Editar información
              </button>
            )}
          </div>

          {generalSuccess && (
            <div
              className="form-message form-message--success"
              role="status"
            >
              {generalSuccess}
            </div>
          )}

          {generalError
            && !isGeneralFormOpen && (
            <div
              className="form-message form-message--error"
              role="alert"
            >
              {generalError}
            </div>
          )}

          {isGeneralFormOpen && (
            <div className="student-record-card__content">
              <h3 className="student-record-form-title">
                Editar información general
              </h3>

              <StudentEditForm
                key={`edit-general-${studentId}`}
                student={general}
                onSubmit={handleGeneralSubmit}
                onCancel={handleGeneralCancel}
                isSubmitting={isSavingGeneral}
                error={generalError}
              />
            </div>
          )}

          {!isGeneralFormOpen && (
            <dl className="student-record-grid">
              <div>
                <dt>Código institucional</dt>
                <dd>
                  {general.institutional_code}
                </dd>
              </div>

              <div>
                <dt>Nombres</dt>
                <dd>{general.first_name}</dd>
              </div>

              <div>
                <dt>Apellidos</dt>
                <dd>{general.last_name}</dd>
              </div>

              <div>
                <dt>Fecha de nacimiento</dt>
                <dd>
                  {formatDate(
                    general.date_of_birth
                  )}
                </dd>
              </div>

              <div>
                <dt>Fecha de ingreso</dt>
                <dd>
                  {formatDate(
                    general.admission_date
                  )}
                </dd>
              </div>

              <div>
                <dt>Estado</dt>
                <dd>
                  <span
                    className={
                      general.is_active
                        ? 'status status--active'
                        : 'status status--inactive'
                    }
                  >
                    {general.is_active
                      ? 'Activo'
                      : 'Inactivo'}
                  </span>
                </dd>
              </div>
            </dl>
          )}

          </section>

          {family && (
            <section
              className="student-record-card"
              aria-labelledby="family-section-title"
            >
              <div
                className={
                  'student-record-card__header '
                  + 'student-record-card__header--actions'
                }
              >
                <div>
                  <h2 id="family-section-title">
                    Información familiar
                  </h2>

                  <p>
                    Familiares y contactos asociados al estudiante.
                  </p>
                </div>

                {canManageFamily && !isFamilyFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={handleOpenFamilyRegistration}
                  >
                    Registrar familiar
                  </button>
                )}
              </div>

              {familySuccess && (
                <div
                  className="form-message form-message--success"
                  role="status"
                >
                  {familySuccess}
                </div>
              )}

              {familyError && !isFamilyFormOpen && (
                <div
                  className="form-message form-message--error"
                  role="alert"
                >
                  {familyError}
                </div>
              )}

              {canManageFamily && isFamilyFormOpen && (
                <div className="student-record-card__content">
                  <h3 className="student-record-form-title">
                    {editingFamilyMember
                      ? 'Editar familiar'
                      : 'Nuevo familiar'}
                  </h3>

                  <StudentFamilyMemberForm
                    key={editingFamilyMember?.id ?? 'new'}
                    initialData={editingFamilyMember}
                    onSubmit={handleFamilySubmit}
                    onCancel={handleFamilyCancel}
                    isSubmitting={isSavingFamily}
                    error={familyError}
                  />
                </div>
              )}

              {!isFamilyFormOpen && (
                <StudentFamilyMemberList
                familyMembers={familyItems}
                canManage={canManageFamily}
                onEdit={handleFamilyEdit}
                onDeactivate={handleFamilyDeactivate}
                deactivatingId={
                  deactivatingFamilyMemberId
                }
              />
              )}
            </section>
          )}

          {assignments && (
            <section
              className="student-record-card"
              aria-labelledby="assignments-section-title"
            >
              <div className="student-record-card__header">
                <h2 id="assignments-section-title">
                  Asignaciones profesionales
                </h2>

                <p>
                  Historial de profesionales asignados al
                  estudiante.
                </p>
              </div>

              <StudentRecordAssignmentHistory
                assignments={assignmentItems}
              />
            </section>
          )}

          {academic && (
            <section
              className={
                'student-record-card '
                + 'student-record-card--academic'
              }
              aria-labelledby="academic-section-title"
            >
              <div
                className={
                  'student-record-card__header '
                  + 'student-record-card__header--actions'
                }
              >
                <div>
                  <h2 id="academic-section-title">
                    Información académica
                  </h2>

                  <p>
                    Historial de seguimiento académico
                    del estudiante.
                  </p>
                </div>

                {canManageAcademic
                  && general.is_active
                  && !isAcademicFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={
                      handleNewAcademicFollowUp
                    }
                  >
                    Registrar seguimiento
                  </button>
                )}
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se
                  pueden registrar nuevos seguimientos
                  académicos.
                </div>
              )}

              {academicSuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-academic-message'
                  }
                  role="status"
                >
                  {academicSuccess}
                </div>
              )}

              {academicError
                && !isAcademicFormOpen && (
                <div
                  className={
                    'form-message '
                    + 'form-message--error '
                    + 'student-record-academic-message'
                  }
                  role="alert"
                >
                  {academicError}
                </div>
              )}

              {isAcademicFormOpen && (
                <div className="student-record-card__content">
                  <h3 className="student-record-form-title">
                    {editingFollowUp
                      ? 'Editar seguimiento académico'
                      : 'Nuevo seguimiento académico'}
                  </h3>

                  <AcademicFollowUpForm
                    key={
                      editingFollowUp
                        ? `edit-${editingFollowUp.id}`
                        : 'new'
                    }
                    initialFollowUp={
                      editingFollowUp
                    }
                    onSubmit={
                      handleAcademicSubmit
                    }
                    onCancel={
                      handleAcademicCancel
                    }
                    isSubmitting={
                      isSavingAcademic
                    }
                    error={academicError}
                  />
                </div>
              )}

              <AcademicFollowUpList
                followups={academicFollowUps}
                onEdit={
                  canManageAcademic
                    ? handleAcademicEdit
                    : undefined
                }
              />
            </section>
          )}

          {psychological && (
            <section
              className="student-record-card"
              aria-labelledby="psychological-section-title"
            >
              <div
                className={
                  'student-record-card__header '
                  + 'student-record-card__header--actions'
                }
              >
                <div>
                  <h2 id="psychological-section-title">
                    Información psicológica
                  </h2>

                  <p>
                    Historial de seguimiento psicológico
                    del estudiante.
                  </p>
                </div>

                {canManagePsychological
                  && general.is_active
                  && !isPsychologicalFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={
                      handleNewPsychologicalFollowUp
                    }
                  >
                    Registrar seguimiento
                  </button>
                )}
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se
                  pueden registrar nuevos seguimientos
                  psicológicos.
                </div>
              )}

              {psychologicalSuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-academic-message'
                  }
                  role="status"
                >
                  {psychologicalSuccess}
                </div>
              )}

              {psychologicalError
                && !isPsychologicalFormOpen && (
                <div
                  className={
                    'form-message '
                    + 'form-message--error '
                    + 'student-record-academic-message'
                  }
                  role="alert"
                >
                  {psychologicalError}
                </div>
              )}

              {isPsychologicalFormOpen && (
                <div className="student-record-card__content">
                  <h3 className="student-record-form-title">
                    {editingPsychologicalFollowUp
                      ? 'Editar seguimiento psicológico'
                      : 'Nuevo seguimiento psicológico'}
                  </h3>

                  <PsychologicalFollowUpForm
                    key={
                      editingPsychologicalFollowUp
                        ? `edit-${editingPsychologicalFollowUp.id}`
                        : 'new'
                    }
                    initialFollowUp={
                      editingPsychologicalFollowUp
                    }
                    onSubmit={
                      handlePsychologicalSubmit
                    }
                    onCancel={
                      handlePsychologicalCancel
                    }
                    isSubmitting={
                      isSavingPsychological
                    }
                    error={psychologicalError}
                  />
                </div>
              )}

              <PsychologicalFollowUpList
                followups={psychologicalFollowUps}
                onEdit={
                  canManagePsychological
                    ? handlePsychologicalEdit
                    : undefined
                }
              />
            </section>
          )}

          {therapy && (
            <section
              className="student-record-card"
              aria-labelledby="therapy-section-title"
            >
              <div
                className={
                  'student-record-card__header '
                  + 'student-record-card__header--actions'
                }
              >
                <div>
                  <h2 id="therapy-section-title">
                    Información terapéutica
                  </h2>

                  <p>
                    Historial de seguimiento terapéutico
                    del estudiante.
                  </p>
                </div>

                {canManageTherapy
                  && general.is_active
                  && !isTherapyFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={
                      handleNewTherapyFollowUp
                    }
                  >
                    Registrar seguimiento
                  </button>
                )}
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se
                  pueden registrar nuevos seguimientos
                  terapéuticos.
                </div>
              )}

              {therapySuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-academic-message'
                  }
                  role="status"
                >
                  {therapySuccess}
                </div>
              )}

              {therapyError
                && !isTherapyFormOpen && (
                <div
                  className={
                    'form-message '
                    + 'form-message--error '
                    + 'student-record-academic-message'
                  }
                  role="alert"
                >
                  {therapyError}
                </div>
              )}

              {isTherapyFormOpen && (
                <div className="student-record-card__content">
                  <h3 className="student-record-form-title">
                    {editingTherapyFollowUp
                      ? 'Editar seguimiento terapéutico'
                      : 'Nuevo seguimiento terapéutico'}
                  </h3>

                  <TherapyFollowUpForm
                    key={
                      editingTherapyFollowUp
                        ? `edit-${editingTherapyFollowUp.id}`
                        : 'new'
                    }
                    initialFollowUp={
                      editingTherapyFollowUp
                    }
                    onSubmit={
                      handleTherapySubmit
                    }
                    onCancel={
                      handleTherapyCancel
                    }
                    isSubmitting={
                      isSavingTherapy
                    }
                    error={therapyError}
                  />
                </div>
              )}

              <TherapyFollowUpList
                followups={therapyFollowUps}
                onEdit={
                  canManageTherapy
                    ? handleTherapyEdit
                    : undefined
                }
              />
            </section>
          )}

          <section
            className="student-record-card"
            aria-labelledby="documents-section-title"
          >
            <div
              className={
                'student-record-card__header '
                + 'student-record-card__header--actions'
              }
            >
              <div>
                <h2 id="documents-section-title">
                  Documentos
                </h2>

                <p>
                  Consulta, carga y descarga de documentos
                  asociados al expediente del estudiante.
                </p>
              </div>

              {!isDocumentFormOpen && (
                <button
                  className="button button--primary"
                  type="button"
                  onClick={handleOpenDocumentUpload}
                >
                  Cargar documento
                </button>
              )}
            </div>

            {documentSuccess && (
              <div
                className="form-message form-message--success"
                role="status"
              >
                {documentSuccess}
              </div>
            )}

            {documentError
              && !isDocumentFormOpen && (
              <div
                className="form-message form-message--error"
                role="alert"
              >
                {documentError}
              </div>
            )}

            {isDocumentFormOpen && (
              <div className="student-record-card__content">
                <h3 className="student-record-form-title">
                  Cargar documento
                </h3>

                <StudentDocumentUploadForm
                  key={`document-upload-${studentContext}`}
                  context={studentContext}
                  onSubmit={handleDocumentSubmit}
                  onCancel={handleDocumentCancel}
                  isSubmitting={isSavingDocument}
                  error={documentError}
                />
              </div>
            )}

            {documentQueryError && (
              <div
                className="form-message form-message--error"
                role="alert"
              >
                {documentQueryError}
              </div>
            )}

            <StudentDocumentList
              documents={documents}
              isLoading={isLoadingDocuments}
              onDownload={handleDocumentDownload}
              downloadingId={
                downloadingDocumentId
              }
            />

          </section>

        {evaluationSection && (
          <section
            className="student-record-card"
            aria-labelledby="evaluations-section-title"
          >
            <div
              className={
                'student-record-card__header '
                + 'student-record-card__header--actions'
              }
            >
              <div>
                <h2 id="evaluations-section-title">
                  Evaluaciones
                </h2>

                <p>
                  Resultados y observaciones de las evaluaciones
                  realizadas al estudiante.
                </p>
              </div>

              {canManageEvaluations
                && general.is_active
                && !isEvaluationFormOpen && (
                <button
                  className="button button--primary"
                  type="button"
                  onClick={handleNewEvaluation}
                >
                  Registrar evaluación
                </button>
              )}
            </div>

            {evaluationSuccess && (
              <div
                className="form-message form-message--success"
                role="status"
              >
                {evaluationSuccess}
              </div>
            )}

            {evaluationError
              && !isEvaluationFormOpen && (
              <div
                className="form-message form-message--error"
                role="alert"
              >
                {evaluationError}
              </div>
            )}

            {isEvaluationFormOpen && (
              <div className="student-record-card__content">
                <h3 className="student-record-form-title">
                  {editingEvaluation
                    ? 'Editar evaluación'
                    : 'Registrar evaluación'}
                </h3>

                <EvaluationForm
                  key={
                    editingEvaluation
                      ? `edit-${editingEvaluation.id}`
                      : 'new'
                  }
                  initialEvaluation={editingEvaluation}
                  onSubmit={handleEvaluationSubmit}
                  onCancel={handleEvaluationCancel}
                  isSubmitting={isSavingEvaluation}
                  error={evaluationError}
                />
              </div>
            )}

            <EvaluationList
              evaluations={evaluationItems}
              onEdit={
                canManageEvaluations
                  ? handleEvaluationEdit
                  : undefined
              }
            />
          </section>
        )}
        </>
      )}
    </main>
  )
}


export default StudentRecordPage
