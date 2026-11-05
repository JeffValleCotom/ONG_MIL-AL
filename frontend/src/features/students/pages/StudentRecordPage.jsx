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
import StudentHistoryTimeline
  from '../components/StudentHistoryTimeline'
import StudentEvolutionPanel
  from '../components/StudentEvolutionPanel'
import AIInsightPanel
  from '../../aiSupport/components/AIInsightPanel'
import StudentInterventionPanel
  from '../components/StudentInterventionPanel'
import AppModal
  from '../../../components/ui/AppModal'


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
  const [activeTab, setActiveTab] =
  useState('summary')
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
    isDocumentListOpen,
    setIsDocumentListOpen,
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
        setFamilyError(
          getFamilyErrorMessage(error)
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
    if (isSavingFamily) {
      return
    }

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
  const canManageInterventions = Boolean(
    capabilities.manage_interventions
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
  const history = record?.sections?.history
  const evolution = record?.sections?.evolution
  const interventionSection =
    record?.sections?.interventions

  const assignmentItems =
    assignments?.items ?? []
  const familyItems =
    family?.items ?? []

  const academicFollowUps =
    academic?.followups ?? []
  const psychologicalFollowUps =
    psychological?.followups ?? []
  const latestAcademicFollowUp =
    academicFollowUps.reduce(
      (latest, followUp) => {
        if (!latest) {
          return followUp
        }

        return followUp.followup_date
          > latest.followup_date
          ? followUp
          : latest
      },
      null,
    )
  const latestPsychologicalFollowUp =
    psychologicalFollowUps.reduce(
      (latest, followUp) => {
        if (!latest) {
          return followUp
        }

        return followUp.followup_date
          > latest.followup_date
          ? followUp
          : latest
      },
      null,
    )
  const therapyFollowUps =
    therapy?.followups ?? []
  const latestTherapyFollowUp =
    therapyFollowUps.reduce(
      (latest, followUp) => {
        if (!latest) {
          return followUp
        }

        return followUp.followup_date
          > latest.followup_date
          ? followUp
          : latest
      },
      null,
    )
  const evaluationItems =
    evaluationSection?.items ?? []
  const latestEvaluation =
    evaluationItems.reduce(
      (latest, evaluation) => {
        if (!latest) {
          return evaluation
        }

        return evaluation.evaluation_date
          > latest.evaluation_date
          ? evaluation
          : latest
      },
      null,
    )
  const historyItems =
  history?.items ?? []
  const performedInterventions =
    interventionSection?.performed ?? []

  const plannedInterventions =
    interventionSection?.planned ?? []

  const interventionResponsibleOptions =
    interventionSection?.responsible_options ?? []

  const canUseAISupport = [
    'DOCENTE',
    'PSICOLOGO',
    'TERAPEUTA',
  ].includes(studentContext)

  const recordTabs = [
    {
      id: 'summary',
      label: 'Resumen',
      visible: true,
    },
    {
      id: 'academic',
      label: 'Académico',
      visible: Boolean(academic),
    },
    {
      id: 'psychological',
      label: 'Psicológico',
      visible: Boolean(psychological),
    },
    {
      id: 'therapy',
      label: 'Terapéutico',
      visible: Boolean(therapy),
    },
    {
      id: 'evaluations',
      label: 'Evaluaciones',
      visible: Boolean(evaluationSection),
    },
    {
      id: 'interventions',
      label: 'Intervenciones',
      visible: Boolean(interventionSection),
    },
  ].filter((tab) => tab.visible)

  return (
    <main className="student-record-page">
      {general && (
        <section className="student-record-hero">
          <div className="student-record-hero__identity">
            <div
              className="student-record-hero__avatar"
              aria-hidden="true"
            >
              {general.first_name?.[0]}
              {general.last_name?.[0]}
            </div>

            <div>
              <div className="student-record-hero__name-row">
                <h2>
                  {general.first_name}{' '}
                  {general.last_name}
                </h2>

                <span
                  className={
                    general.is_active
                      ? 'student-record-status student-record-status--active'
                      : 'student-record-status student-record-status--inactive'
                  }
                >
                  {general.is_active
                    ? 'Activo'
                    : 'Inactivo'}
                </span>
              </div>

              <p>
                {general.institutional_code}
                {record?.context
                  ? ` · ${record.context}`
                  : ''}
              </p>
            </div>
          </div>

          <div className="student-record-hero__actions">
            {(history || evolution) && (
              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  setActiveTab('evolution')
                }}
              >
                Ver evolución
              </button>
            )}

            {canUseAISupport && (
              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  setActiveTab('ai')
                }}
              >
                Asistente IA
              </button>
            )}

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
              ← Volver a estudiantes
            </button>
          </div>
        </section>
      )}

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
        <nav
          className="student-record-tabs"
          aria-label="Secciones del expediente"
        >
          {recordTabs.map((tab) => (
            <button
              key={tab.id}
              className={
                activeTab === tab.id
                  ? 'student-record-tab student-record-tab--active'
                  : 'student-record-tab'
              }
              type="button"
              onClick={() => {
                setActiveTab(tab.id)
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div
          className={
            activeTab === 'summary'
              ? (
                  'student-record-tab-content '
                  + 'student-record-tab-content--summary'
                )
              : 'student-record-tab-content'
          }
        >
        {activeTab === 'summary' && (
          <section
            className={
              'student-record-card '
              + 'student-record-summary-card '
              + 'student-record-summary-card--general'
            }
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

            {isGeneralFormOpen ? (
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
            ) : (
              <dl className="student-record-grid">
                <div>
                  <dt>Código institucional</dt>
                  <dd>
                    {general.institutional_code || '—'}
                  </dd>
                </div>

                <div>
                  <dt>Nombre completo</dt>
                  <dd>
                    {general.first_name}{' '}
                    {general.last_name}
                  </dd>
                </div>

                <div>
                  <dt>Fecha de nacimiento</dt>
                  <dd>
                    {formatDate(general.date_of_birth)}
                  </dd>
                </div>

                <div>
                  <dt>Fecha de ingreso</dt>
                  <dd>
                    {formatDate(general.admission_date)}
                  </dd>
                </div>

                <div>
                  <dt>Estado</dt>
                  <dd>
                    <span
                      className={
                        general.is_active
                          ? (
                              'student-record-status '
                              + 'student-record-status--active'
                            )
                          : (
                              'student-record-status '
                              + 'student-record-status--inactive'
                            )
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
        )}

        {activeTab === 'summary' && (
          <section
            className={
              'student-record-card '
              + 'student-record-summary-card '
              + 'student-record-summary-card--status'
            }
            aria-labelledby="status-section-title"
          >
            <div className="student-record-summary-status">
              <div>
                <p className="student-record-summary-status__eyebrow">
                  Estado de seguimiento
                </p>

                <h2 id="status-section-title">
                  {general.is_active
                    ? 'En seguimiento'
                    : 'Estudiante inactivo'}
                </h2>
              </div>

              <span
                className={
                  general.is_active
                    ? (
                        'student-record-summary-status__badge '
                        + 'student-record-summary-status__badge--active'
                      )
                    : (
                        'student-record-summary-status__badge '
                        + 'student-record-summary-status__badge--inactive'
                      )
                }
              >
                {general.is_active
                  ? 'Activo'
                  : 'Inactivo'}
              </span>
            </div>

            <p className="student-record-summary-status__copy">
              Consulta las áreas de seguimiento desde las
              pestañas superiores del expediente.
            </p>
          </section>
        )}
          {activeTab === 'summary' && (
            <section
              className={
                'student-record-card '
                + 'student-record-summary-card '
                + 'student-record-summary-card--family'
              }
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

                {family
                  && familyItems.length > 0
                  && canManageFamily
                  && !isFamilyFormOpen && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={handleOpenFamilyRegistration}
                  >
                    Registrar familiar
                  </button>
                )}
              </div>

              {!family && (
                <div className="student-record-summary-empty">
                  <span
                    className="student-record-summary-empty__icon"
                    aria-hidden="true"
                  >
                    ○
                  </span>

                  <strong>No disponible</strong>

                  <p>
                    La información familiar no está disponible
                    en este espacio de trabajo.
                  </p>
                </div>
              )}

              {family && familyItems.length === 0
                && !isFamilyFormOpen && (
                  <div className="student-record-summary-empty">
                    <span
                      className="student-record-summary-empty__icon"
                      aria-hidden="true"
                    >
                      +
                    </span>

                    <strong>Sin familiares registrados</strong>

                    <p>
                      Aún no se han registrado familiares o
                      contactos asociados al estudiante.
                    </p>

                    {canManageFamily && (
                      <button
                        className="button button--primary"
                        type="button"
                        onClick={handleOpenFamilyRegistration}
                      >
                        Registrar familiar
                      </button>
                    )}
                  </div>
              )}

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

              {family
                && familyItems.length > 0
                && !isFamilyFormOpen && (
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

          {activeTab === 'summary' && (
            <section
              className={
                'student-record-card '
                + 'student-record-summary-card '
                + 'student-record-summary-card--assignments'
              }
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

              {assignments ? (
                assignmentItems.length > 0 ? (
                  <StudentRecordAssignmentHistory
                    assignments={assignmentItems}
                  />
                ) : (
                  <div className="student-record-summary-empty">
                    <span
                      className="student-record-summary-empty__icon"
                      aria-hidden="true"
                    >
                      ○
                    </span>

                    <strong>Sin asignaciones registradas</strong>

                    <p>
                      No hay profesionales asignados al
                      estudiante en este momento.
                    </p>
                  </div>
                )
              ) : (
                <div className="student-record-summary-empty">
                  <span
                    className="student-record-summary-empty__icon"
                    aria-hidden="true"
                  >
                    ○
                  </span>

                  <strong>No disponible</strong>

                  <p>
                    Las asignaciones profesionales no están
                    disponibles en este espacio de trabajo.
                  </p>
                </div>
              )}
            </section>
          )}

          {activeTab === 'academic' && academic && (
            <section
              className="student-record-academic"
              aria-labelledby="academic-section-title"
            >
              <div className="student-record-section-heading">
                <div>
                  <p className="student-record-section-heading__eyebrow">
                    Seguimiento educativo
                  </p>

                  <h2 id="academic-section-title">
                    Seguimiento académico
                  </h2>

                  <p>
                    Consulta el desempeño, fortalezas y áreas
                    de mejora registradas durante el proceso.
                  </p>
                </div>

                {canManageAcademic
                  && general.is_active && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={handleNewAcademicFollowUp}
                  >
                    + Nuevo seguimiento
                  </button>
                )}
              </div>

              <div className="student-record-academic__stats">
                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◫
                  </span>

                  <div>
                    <strong>
                      {academicFollowUps.length}
                    </strong>

                    <span>
                      Seguimientos registrados
                    </span>
                  </div>
                </article>

                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◷
                  </span>

                  <div>
                    <strong>
                      {latestAcademicFollowUp
                        ? formatDate(
                            latestAcademicFollowUp.followup_date,
                          )
                        : '—'}
                    </strong>

                    <span>
                      Último seguimiento
                    </span>
                  </div>
                </article>

                <article
                  className={
                    'student-record-mini-stat '
                    + 'student-record-mini-stat--status'
                  }
                >
                  <span className="student-record-mini-stat__icon">
                    ↗
                  </span>

                  <div>
                    <strong>
                      {general.is_active
                        ? 'En seguimiento'
                        : 'Inactivo'}
                    </strong>

                    <span>
                      Estado del estudiante
                    </span>
                  </div>
                </article>
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se pueden
                  registrar nuevos seguimientos académicos.
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

              <section
                className={
                  'student-record-card '
                  + 'student-record-academic__history-card'
                }
              >
                <div className="student-record-card__header">
                  <div>
                    <h3>
                      Historial académico
                    </h3>

                    <p>
                      Seguimientos registrados por materia
                      o área académica.
                    </p>
                  </div>
                </div>

                <AcademicFollowUpList
                  followups={academicFollowUps}
                  onEdit={
                    canManageAcademic
                      ? handleAcademicEdit
                      : undefined
                  }
                />
              </section>

              <AppModal
                isOpen={isAcademicFormOpen}
                title={
                  editingFollowUp
                    ? 'Editar seguimiento académico'
                    : 'Nuevo seguimiento académico'
                }
                subtitle={
                  editingFollowUp
                    ? (
                        'Actualiza la información académica '
                        + 'registrada para este seguimiento.'
                      )
                    : (
                        'Registra el desempeño y las '
                        + 'observaciones académicas.'
                      )
                }
                onClose={handleAcademicCancel}
                closeDisabled={isSavingAcademic}
                size="lg"
              >
                <AcademicFollowUpForm
                  key={
                    editingFollowUp
                      ? `edit-${editingFollowUp.id}`
                      : 'new'
                  }
                  initialFollowUp={editingFollowUp}
                  onSubmit={handleAcademicSubmit}
                  onCancel={handleAcademicCancel}
                  isSubmitting={isSavingAcademic}
                  error={academicError}
                />
              </AppModal>
            </section>
          )}

          {activeTab === 'psychological' && psychological && (
            <section
              className="student-record-psychological"
              aria-labelledby="psychological-section-title"
            >
              <div className="student-record-section-heading">
                <div>
                  <p className="student-record-section-heading__eyebrow">
                    Seguimiento profesional
                  </p>

                  <h2 id="psychological-section-title">
                    Seguimiento psicológico
                  </h2>

                  <p>
                    Consulta observaciones, notas emocionales
                    y recomendaciones registradas durante
                    el seguimiento.
                  </p>
                </div>

                {canManagePsychological
                  && general.is_active && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={
                      handleNewPsychologicalFollowUp
                    }
                  >
                    + Nuevo seguimiento
                  </button>
                )}
              </div>

              <div className="student-record-psychological__stats">
                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◫
                  </span>

                  <div>
                    <strong>
                      {psychologicalFollowUps.length}
                    </strong>

                    <span>
                      Seguimientos registrados
                    </span>
                  </div>
                </article>

                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◷
                  </span>

                  <div>
                    <strong>
                      {latestPsychologicalFollowUp
                        ? formatDate(
                            latestPsychologicalFollowUp
                              .followup_date,
                          )
                        : '—'}
                    </strong>

                    <span>
                      Último seguimiento
                    </span>
                  </div>
                </article>

                <article
                  className={
                    'student-record-mini-stat '
                    + 'student-record-mini-stat--status'
                  }
                >
                  <span className="student-record-mini-stat__icon">
                    ↗
                  </span>

                  <div>
                    <strong>
                      {general.is_active
                        ? 'En seguimiento'
                        : 'Inactivo'}
                    </strong>

                    <span>
                      Estado del estudiante
                    </span>
                  </div>
                </article>
              </div>

              {!general.is_active && (
                <div className="student-record-academic-note">
                  El estudiante está inactivo. No se pueden
                  registrar nuevos seguimientos psicológicos.
                </div>
              )}

              {psychologicalSuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-psychological__message'
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
                    + 'student-record-psychological__message'
                  }
                  role="alert"
                >
                  {psychologicalError}
                </div>
              )}

              <section
                className={
                  'student-record-card '
                  + 'student-record-psychological__history-card'
                }
              >
                <div className="student-record-card__header">
                  <div>
                    <h3>
                      Historial psicológico
                    </h3>

                    <p>
                      Seguimientos profesionales registrados
                      para el estudiante.
                    </p>
                  </div>
                </div>

                <PsychologicalFollowUpList
                  followups={psychologicalFollowUps}
                  onEdit={
                    canManagePsychological
                      ? handlePsychologicalEdit
                      : undefined
                  }
                />
              </section>

              <AppModal
                isOpen={isPsychologicalFormOpen}
                title={
                  editingPsychologicalFollowUp
                    ? 'Editar seguimiento psicológico'
                    : 'Nuevo seguimiento psicológico'
                }
                subtitle={
                  editingPsychologicalFollowUp
                    ? (
                        'Actualiza la información registrada '
                        + 'para este seguimiento.'
                      )
                    : (
                        'Registra una nueva observación '
                        + 'de seguimiento psicológico.'
                      )
                }
                onClose={handlePsychologicalCancel}
                closeDisabled={isSavingPsychological}
                size="lg"
              >
                <PsychologicalFollowUpForm
                  key={
                    editingPsychologicalFollowUp
                      ? (
                          `edit-${
                            editingPsychologicalFollowUp.id
                          }`
                        )
                      : 'new'
                  }
                  initialFollowUp={
                    editingPsychologicalFollowUp
                  }
                  onSubmit={handlePsychologicalSubmit}
                  onCancel={handlePsychologicalCancel}
                  isSubmitting={isSavingPsychological}
                  error={psychologicalError}
                />
              </AppModal>
            </section>
          )}

          {activeTab === 'therapy' && therapy && (
            <section
              className="student-record-therapy"
              aria-labelledby="therapy-section-title"
            >
              <div className="student-record-section-heading">
                <div>
                  <p className="student-record-section-heading__eyebrow">
                    Seguimiento profesional
                  </p>

                  <h2 id="therapy-section-title">
                    Seguimiento terapéutico
                  </h2>

                  <p>
                    Registra sesiones y consulta el historial
                    terapéutico disponible del estudiante.
                  </p>
                </div>
                {canManageTherapy
                  && general.is_active && (
                  <button
                    className="button button--primary"
                    type="button"
                    onClick={handleNewTherapyFollowUp}
                  >
                    + Nuevo seguimiento
                  </button>
                )}
              </div>

              <div className="student-record-therapy__stats">
                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◫
                  </span>

                  <div>
                    <strong>
                      {therapyFollowUps.length}
                    </strong>

                    <span>
                      Sesiones registradas
                    </span>
                  </div>
                </article>

                <article className="student-record-mini-stat">
                  <span className="student-record-mini-stat__icon">
                    ◷
                  </span>

                  <div>
                    <strong>
                      {latestTherapyFollowUp
                        ? formatDate(
                            latestTherapyFollowUp.followup_date,
                          )
                        : '—'}
                    </strong>

                    <span>
                      Última sesión
                    </span>
                  </div>
                </article>

                <article
                  className={
                    'student-record-mini-stat '
                    + 'student-record-mini-stat--status'
                  }
                >
                  <span className="student-record-mini-stat__icon">
                    ↗
                  </span>

                  <div>
                    <strong>
                      {general.is_active
                        ? 'En seguimiento'
                        : 'Inactivo'}
                    </strong>

                    <span>
                      Estado del estudiante
                    </span>
                  </div>
                </article>
              </div>
              {therapySuccess && (
                <div
                  className={
                    'form-message '
                    + 'form-message--success '
                    + 'student-record-therapy__message'
                  }
                  role="status"
                >
                  {therapySuccess}
                </div>
              )}
              <div className="student-record-therapy__workspace">
                <section
                  className={
                    'student-record-card '
                    + 'student-record-therapy__history-card'
                  }
                >
                  <div className="student-record-card__header">
                    <div>
                      <h3>Historial de sesiones</h3>

                      <p>
                        Seguimientos registrados en orden
                        cronológico.
                      </p>
                    </div>
                  </div>

                  <TherapyFollowUpList
                    followups={therapyFollowUps}
                    onEdit={
                      canManageTherapy
                        ? handleTherapyEdit
                        : undefined
                    }
                  />
                </section>
              </div>
              <AppModal
                isOpen={isTherapyFormOpen}
                title={
                  editingTherapyFollowUp
                    ? 'Editar seguimiento terapéutico'
                    : 'Nuevo seguimiento terapéutico'
                }
                subtitle={
                  editingTherapyFollowUp
                    ? 'Actualiza la información registrada durante la sesión.'
                    : 'Registra la información de una nueva sesión terapéutica.'
                }
                onClose={handleTherapyCancel}
                closeDisabled={isSavingTherapy}
                size="lg"
              >
                <TherapyFollowUpForm
                  key={
                    editingTherapyFollowUp
                      ? `edit-${editingTherapyFollowUp.id}`
                      : 'new'
                  }
                  initialFollowUp={
                    editingTherapyFollowUp
                  }
                  onSubmit={handleTherapySubmit}
                  onCancel={handleTherapyCancel}
                  isSubmitting={isSavingTherapy}
                  error={therapyError}
                />
              </AppModal>
            </section>
          )}

        {activeTab === 'summary' && (
          <section
            className={
              'student-record-card '
              + 'student-record-summary-card '
              + 'student-record-summary-card--documents'
            }
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

            <div className="student-record-documents-summary">
              <div className="student-record-documents-summary__count">
                <span
                  className="student-record-documents-summary__icon"
                  aria-hidden="true"
                >
                  ▣
                </span>

                <div>
                  <strong>
                    {isLoadingDocuments
                      ? 'Cargando documentos...'
                      : (
                          `${documents.length} ${
                            documents.length === 1
                              ? 'documento disponible'
                              : 'documentos disponibles'
                          }`
                        )}
                  </strong>

                  <p>
                    Consulta y descarga los archivos asociados
                    al expediente del estudiante.
                  </p>
                </div>
              </div>

              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  setIsDocumentListOpen(true)
                }}
                disabled={isLoadingDocuments}
              >
                Ver documentos
              </button>
            </div>

            <AppModal
              isOpen={isDocumentFormOpen}
              title="Cargar documento"
              subtitle={
                'Agrega un documento asociado al '
                + 'expediente del estudiante.'
              }
              onClose={handleDocumentCancel}
              closeDisabled={isSavingDocument}
              size="md"
            >
              <StudentDocumentUploadForm
                key={`document-upload-${studentContext}`}
                context={studentContext}
                onSubmit={handleDocumentSubmit}
                onCancel={handleDocumentCancel}
                isSubmitting={isSavingDocument}
                error={documentError}
              />
            </AppModal>

            <AppModal
              isOpen={isDocumentListOpen}
              title="Documentos del estudiante"
              subtitle={
                'Consulta y descarga los documentos '
                + 'asociados al expediente.'
              }
              onClose={() => {
                setIsDocumentListOpen(false)
              }}
              size="lg"
            >
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
            </AppModal>

          </section>
        )}

        {activeTab === 'evaluations'
          && evaluationSection && (
          <section
            className="student-record-evaluations"
            aria-labelledby="evaluations-section-title"
          >
            <div className="student-record-section-heading">
              <div>
                <p className="student-record-section-heading__eyebrow">
                  Valoraciones profesionales
                </p>

                <h2 id="evaluations-section-title">
                  Evaluaciones del estudiante
                </h2>

                <p>
                  Consulta resultados, observaciones y
                  evaluaciones registradas durante el proceso
                  de seguimiento.
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
                  + Registrar evaluación
                </button>
              )}
            </div>

            <div className="student-record-evaluations__stats">
              <article className="student-record-mini-stat">
                <span className="student-record-mini-stat__icon">
                  ✓
                </span>

                <div>
                  <strong>
                    {evaluationItems.length}
                  </strong>

                  <span>
                    Evaluaciones registradas
                  </span>
                </div>
              </article>

              <article className="student-record-mini-stat">
                <span className="student-record-mini-stat__icon">
                  ◷
                </span>

                <div>
                  <strong>
                    {latestEvaluation
                      ? formatDate(
                          latestEvaluation.evaluation_date,
                        )
                      : '—'}
                  </strong>

                  <span>
                    Última evaluación
                  </span>
                </div>
              </article>

              <article
                className={
                  'student-record-mini-stat '
                  + 'student-record-mini-stat--status'
                }
              >
                <span className="student-record-mini-stat__icon">
                  ↗
                </span>

                <div>
                  <strong>
                    {general.is_active
                      ? 'En seguimiento'
                      : 'Inactivo'}
                  </strong>

                  <span>
                    Estado del estudiante
                  </span>
                </div>
              </article>
            </div>

            {!general.is_active && (
              <div className="student-record-academic-note">
                El estudiante está inactivo. No se pueden
                registrar nuevas evaluaciones.
              </div>
            )}

            {evaluationSuccess && (
              <div
                className={
                  'form-message '
                  + 'form-message--success '
                  + 'student-record-evaluations__message'
                }
                role="status"
              >
                {evaluationSuccess}
              </div>
            )}

            {evaluationError
              && !isEvaluationFormOpen && (
              <div
                className={
                  'form-message '
                  + 'form-message--error '
                  + 'student-record-evaluations__message'
                }
                role="alert"
              >
                {evaluationError}
              </div>
            )}

            <AppModal
              isOpen={isEvaluationFormOpen}
              title={
                editingEvaluation
                  ? 'Editar evaluación'
                  : 'Registrar evaluación'
              }
              subtitle={
                editingEvaluation
                  ? 'Actualiza los resultados y observaciones de la evaluación.'
                  : 'Registra una nueva evaluación del estudiante.'
              }
              onClose={handleEvaluationCancel}
              closeDisabled={isSavingEvaluation}
              size="md"
            >
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
            </AppModal>

            <section
              className={
                'student-record-card '
                + 'student-record-evaluations__list-card'
              }
            >
              <div className="student-record-card__header">
                <div>
                  <h3>
                    Historial de evaluaciones
                  </h3>

                  <p>
                    Evaluaciones registradas dentro del
                    seguimiento del estudiante.
                  </p>
                </div>
              </div>

              <EvaluationList
                evaluations={evaluationItems}
                onEdit={
                  canManageEvaluations
                    ? handleEvaluationEdit
                    : undefined
                }
              />
            </section>
          </section>
        )}

        {activeTab === 'interventions' && interventionSection && (
          <section
            className="student-record-card"
            aria-labelledby="interventions-section-title"
          >
            <div className="student-record-card__header">
              <div>
                <h2 id="interventions-section-title">
                  Intervenciones
                </h2>

                <p>
                  Planifica acciones de seguimiento y consulta
                  las intervenciones realizadas al estudiante.
                </p>
              </div>
            </div>

            <StudentInterventionPanel
              studentId={studentId}
              context={studentContext}
              performed={performedInterventions}
              planned={plannedInterventions}
              responsibleOptions={
                interventionResponsibleOptions
              }
              canManage={canManageInterventions}
              onChanged={refreshRecord}
            />
          </section>
        )}

        {activeTab === 'evolution'
          && (history || evolution) && (
          <section
            className="student-record-evolution"
            aria-labelledby="evolution-view-title"
          >
            <div className="student-record-section-heading">
              <div>
                <p className="student-record-section-heading__eyebrow">
                  Seguimiento consolidado
                </p>

                <h2 id="evolution-view-title">
                  Evolución del estudiante
                </h2>

                <p>
                  Consulta la actividad registrada,
                  compara períodos y revisa el historial
                  integral del seguimiento.
                </p>
              </div>
            </div>

            <div className="student-record-evolution__workspace">
              {evolution && (
                <section
                  className={
                    'student-record-card '
                    + 'student-record-evolution__card'
                  }
                >
                  <div className="student-record-card__header">
                    <div>
                      <h3>
                        Evolución y progreso
                      </h3>

                      <p>
                        Actividad registrada y comparación
                        entre períodos de seguimiento.
                      </p>
                    </div>
                  </div>

                  <StudentEvolutionPanel
                    evolution={evolution}
                  />
                </section>
              )}

              {history && (
                <section
                  className={
                    'student-record-card '
                    + 'student-record-evolution__card'
                  }
                >
                  <div className="student-record-card__header">
                    <div>
                      <h3>
                        Historial integral
                      </h3>

                      <p>
                        Registros disponibles en orden
                        cronológico dentro del seguimiento.
                      </p>
                    </div>
                  </div>

                  <StudentHistoryTimeline
                    items={historyItems}
                  />
                </section>
              )}
            </div>
          </section>
        )}

        {activeTab === 'ai' && canUseAISupport && (
          <section
            className="student-record-ai"
            aria-labelledby="ai-support-section-title"
          >
            <div className="student-record-section-heading">
              <div>
                <p className="student-record-section-heading__eyebrow">
                  Apoyo profesional
                </p>

                <h2 id="ai-support-section-title">
                  Asistente IA
                </h2>

                <p>
                  Analiza información autorizada del
                  seguimiento como apoyo a la revisión
                  profesional.
                </p>
              </div>
            </div>

            <div
              className={
                'student-record-card '
                + 'student-record-ai__workspace'
              }
            >
              <AIInsightPanel
                studentId={studentId}
                context={studentContext}
              />
            </div>
          </section>
        )}
        </div>
        </>
      )}
    </main>
  )
}


export default StudentRecordPage
