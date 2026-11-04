export const REPORT_TYPE_LABELS = {
  GENERAL: 'General',
  ACADEMIC: 'Académico',
  PSYCHOLOGICAL: 'Psicológico',
  THERAPY: 'Terapéutico',
  INTERVENTIONS: 'Intervenciones',
  INTEGRAL: 'Integral',
}


export const REPORT_TYPES_BY_CONTEXT = {
  DOCENTE: [
    'ACADEMIC',
    'INTEGRAL',
  ],

  PSICOLOGO: [
    'PSYCHOLOGICAL',
    'INTERVENTIONS',
    'INTEGRAL',
  ],

  TERAPEUTA: [
    'THERAPY',
    'INTERVENTIONS',
    'INTEGRAL',
  ],

  RESPONSABLE_INSTITUCIONAL: [
    'GENERAL',
  ],
}
