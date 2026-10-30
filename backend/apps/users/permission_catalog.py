PLATFORM_PERMISSIONS = (
    (
        "manage_users",
        "Puede administrar usuarios institucionales",
    ),
    (
        "manage_roles",
        "Puede administrar roles institucionales",
    ),
    (
        "manage_permissions",
        "Puede administrar permisos institucionales",
    ),
    (
        "view_students",
        "Puede consultar información general de estudiantes",
    ),
    (
        "manage_students",
        "Puede administrar información general de estudiantes",
    ),
    (
        "manage_student_assignments",
        "Puede administrar asignaciones de profesionales a estudiantes",
    ),
    (
        "view_academic_followups",
        "Puede consultar seguimientos académicos",
    ),
    (
        "manage_academic_followups",
        "Puede administrar seguimientos académicos",
    ),
    (
        "view_psychological_followups",
        "Puede consultar seguimientos psicológicos",
    ),
    (
        "manage_psychological_followups",
        "Puede administrar seguimientos psicológicos",
    ),
    (
        "view_evaluations",
        "Puede consultar evaluaciones",
    ),
    (
        "manage_evaluations",
        "Puede administrar evaluaciones",
    ),
    (
        "view_interventions",
        "Puede consultar intervenciones",
    ),
    (
        "manage_interventions",
        "Puede administrar intervenciones",
    ),
    (
        "view_reports",
        "Puede consultar reportes autorizados",
    ),
    (
        "view_dashboard",
        "Puede consultar paneles e indicadores autorizados",
    ),
    (
        "view_alerts",
        "Puede consultar alertas autorizadas",
    ),
    (
        "use_ai_assistant",
        "Puede utilizar el asistente de inteligencia artificial",
    ),
    (
        "view_audit",
        "Puede consultar información de auditoría",
    ),
)


PLATFORM_PERMISSION_CODENAMES = tuple(
    codename
    for codename, _ in PLATFORM_PERMISSIONS
)