from __future__ import annotations

import hashlib
from datetime import date, timedelta

from django.apps import apps
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db import transaction
from django.utils import timezone


DEMO_USER_PREFIX = "demo_seed_"
DEMO_STUDENT_PREFIX = "DEMO-SEED-"

DEMO_USERNAMES = {
    "admin": f"{DEMO_USER_PREFIX}admin",
    "docente": f"{DEMO_USER_PREFIX}docente",
    "psicologo": f"{DEMO_USER_PREFIX}psicologo",
    "terapeuta": f"{DEMO_USER_PREFIX}terapeuta",
    "responsable": f"{DEMO_USER_PREFIX}responsable",
}

DEMO_REFERENCE_DATE = date(2026, 10, 15)


def _model(app_label: str, model_name: str):
    return apps.get_model(app_label, model_name)


def _ensure_groups():
    Group = _model("auth", "Group")

    required = {
        "ADMINISTRADOR",
        "DOCENTE",
        "PSICOLOGO",
        "TERAPEUTA",
        "RESPONSABLE_INSTITUCIONAL",
    }

    groups = {
        group.name: group
        for group in Group.objects.filter(name__in=required)
    }

    missing = required - set(groups)

    if missing:
        raise RuntimeError(
            "Faltan grupos estructurales requeridos: "
            + ", ".join(sorted(missing))
        )

    return groups


def _ensure_users(password: str):
    User = _model("users", "User")
    groups = _ensure_groups()

    definitions = {
        "admin": {
            "username": DEMO_USERNAMES["admin"],
            "first_name": "Administrador",
            "last_name": "Demostración",
            "email": "admin.demo@example.com",
            "group": "ADMINISTRADOR",
        },
        "docente": {
            "username": DEMO_USERNAMES["docente"],
            "first_name": "María",
            "last_name": "Docente Demo",
            "email": "docente.demo@example.com",
            "group": "DOCENTE",
        },
        "psicologo": {
            "username": DEMO_USERNAMES["psicologo"],
            "first_name": "Daniel",
            "last_name": "Psicólogo Demo",
            "email": "psicologo.demo@example.com",
            "group": "PSICOLOGO",
        },
        "terapeuta": {
            "username": DEMO_USERNAMES["terapeuta"],
            "first_name": "Elena",
            "last_name": "Terapeuta Demo",
            "email": "terapeuta.demo@example.com",
            "group": "TERAPEUTA",
        },
        "responsable": {
            "username": DEMO_USERNAMES["responsable"],
            "first_name": "Roberto",
            "last_name": "Responsable Demo",
            "email": "responsable.demo@example.com",
            "group": "RESPONSABLE_INSTITUCIONAL",
        },
    }

    users = {}

    for key, definition in definitions.items():
        user, _ = User.objects.update_or_create(
            username=definition["username"],
            defaults={
                "first_name": definition["first_name"],
                "last_name": definition["last_name"],
                "email": definition["email"],
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )

        user.set_password(password)
        user.save(update_fields=["password"])

        user.groups.set([groups[definition["group"]]])

        users[key] = user

    return users


def _ensure_students():
    Student = _model("students", "Student")

    definitions = [
        {
            "institutional_code": f"{DEMO_STUDENT_PREFIX}001",
            "first_name": "Ana Lucía",
            "last_name": "Morales Pérez",
            "date_of_birth": date(2012, 5, 14),
            "admission_date": date(2024, 1, 15),
        },
        {
            "institutional_code": f"{DEMO_STUDENT_PREFIX}002",
            "first_name": "Diego Alejandro",
            "last_name": "López García",
            "date_of_birth": date(2011, 9, 2),
            "admission_date": date(2023, 2, 1),
        },
        {
            "institutional_code": f"{DEMO_STUDENT_PREFIX}003",
            "first_name": "Sofía Isabel",
            "last_name": "Hernández Ruiz",
            "date_of_birth": date(2013, 1, 23),
            "admission_date": date(2025, 1, 20),
        },
    ]

    students = []

    for definition in definitions:
        student, _ = Student.objects.update_or_create(
            institutional_code=definition["institutional_code"],
            defaults={
                "first_name": definition["first_name"],
                "last_name": definition["last_name"],
                "date_of_birth": definition["date_of_birth"],
                "admission_date": definition["admission_date"],
                "is_active": True,
            },
        )
        students.append(student)

    return students


def _ensure_assignments(students, users):
    Assignment = _model(
        "students",
        "StudentProfessionalAssignment",
    )

    assignments = (
        ("docente", "DOCENTE"),
        ("psicologo", "PSICOLOGO"),
        ("terapeuta", "TERAPEUTA"),
    )

    for student in students:
        for user_key, role in assignments:
            Assignment.objects.update_or_create(
                student=student,
                professional=users[user_key],
                professional_role=role,
                is_active=True,
                defaults={
                    "unassigned_at": None,
                    "assigned_by": users["admin"],
                },
            )


def _ensure_family(students, users):
    FamilyMember = _model(
        "students",
        "StudentFamilyMember",
    )

    definitions = [
        ("Laura", "Pérez Morales", "MADRE"),
        ("José", "López Méndez", "PADRE"),
        ("Claudia", "Ruiz Hernández", "MADRE"),
    ]

    for index, student in enumerate(students):
        first_name, last_name, relationship = definitions[index]

        FamilyMember.objects.update_or_create(
            student=student,
            first_name=first_name,
            last_name=last_name,
            defaults={
                "relationship": relationship,
                "relationship_detail": "",
                "phone": f"+502 5550-010{index + 1}",
                "email": f"familia{index + 1}.demo@example.com",
                "address": "Dirección ficticia para demostración",
                "is_primary_contact": True,
                "is_active": True,
                "deactivated_at": None,
                "created_by": users["admin"],
                "updated_by": users["admin"],
            },
        )


def _ensure_academic_followups(students, users):
    AcademicFollowUp = _model(
        "academic",
        "AcademicFollowUp",
    )

    dates = (
        date(2026, 2, 20),
        date(2026, 5, 20),
        date(2026, 8, 20),
        date(2026, 10, 10),
    )

    observations = (
        "Inicio estable del ciclo. Participa y completa las actividades asignadas.",
        "Se observa mejora progresiva en organización y cumplimiento.",
        "Mantiene avances y solicita apoyo cuando encuentra dificultades.",
        "Cierre del período con progreso sostenido y mayor autonomía.",
    )

    for student_index, student in enumerate(students):
        for index, followup_date in enumerate(dates):
            AcademicFollowUp.objects.update_or_create(
                student=student,
                followup_date=followup_date,
                subject="Matemática",
                defaults={
                    "academic_period": f"Período {index + 1} - 2026",
                    "observations": observations[index],
                    "strengths": (
                        "Participación, disposición para aprender "
                        "y cumplimiento de actividades."
                    ),
                    "areas_for_improvement": (
                        "Reforzar hábitos de estudio y resolución "
                        "autónoma de ejercicios."
                    ),
                    "recommendations": (
                        "Mantener acompañamiento semanal y ejercicios "
                        "de refuerzo."
                    ),
                    "created_by": users["docente"],
                    "updated_by": users["docente"],
                },
            )


def _ensure_psychological_followups(students, users):
    PsychologicalFollowUp = _model(
        "psychology",
        "PsychologicalFollowUp",
    )

    dates = (
        date(2026, 3, 5),
        date(2026, 6, 5),
        date(2026, 9, 5),
    )

    for student in students:
        for index, followup_date in enumerate(dates, start=1):
            PsychologicalFollowUp.objects.update_or_create(
                student=student,
                followup_date=followup_date,
                defaults={
                    "reason": "Seguimiento socioemocional",
                    "observations": (
                        f"Sesión de seguimiento psicológico {index}. "
                        "El estudiante participa adecuadamente."
                    ),
                    "emotional_behavioral_notes": (
                        "Se observan avances graduales en expresión "
                        "emocional y estrategias de autorregulación."
                    ),
                    "recommendations": (
                        "Continuar acompañamiento y reforzar comunicación "
                        "con familia y equipo educativo."
                    ),
                    "created_by": users["psicologo"],
                    "updated_by": users["psicologo"],
                },
            )


def _ensure_therapy_followups(students, users):
    TherapyFollowUp = _model(
        "therapy",
        "TherapyFollowUp",
    )

    dates = (
        date(2026, 3, 15),
        date(2026, 6, 15),
        date(2026, 9, 15),
    )

    for student in students:
        for index, followup_date in enumerate(dates, start=1):
            TherapyFollowUp.objects.update_or_create(
                student=student,
                followup_date=followup_date,
                defaults={
                    "therapy_area": "Habilidades funcionales",
                    "objectives": (
                        "Fortalecer habilidades de atención, seguimiento "
                        "de instrucciones y autonomía."
                    ),
                    "activities": (
                        "Ejercicios estructurados, secuencias de tareas "
                        "y actividades de coordinación."
                    ),
                    "progress_notes": (
                        f"Seguimiento terapéutico {index}: "
                        "progreso observable y participación constante."
                    ),
                    "recommendations": (
                        "Continuar actividades breves y estructuradas "
                        "en el hogar y centro educativo."
                    ),
                    "created_by": users["terapeuta"],
                    "updated_by": users["terapeuta"],
                },
            )


def _ensure_evaluations(students, users):
    Evaluation = _model(
        "evaluations",
        "Evaluation",
    )

    definitions = (
        (
            date(2026, 4, 10),
            "Evaluación académica",
            "DOCENTE",
            "docente",
        ),
        (
            date(2026, 7, 10),
            "Evaluación socioemocional",
            "PSICOLOGO",
            "psicologo",
        ),
        (
            date(2026, 10, 1),
            "Evaluación terapéutica",
            "TERAPEUTA",
            "terapeuta",
        ),
    )

    for student in students:
        for evaluation_date, evaluation_type, role, user_key in definitions:
            Evaluation.objects.update_or_create(
                student=student,
                evaluation_date=evaluation_date,
                evaluation_type=evaluation_type,
                defaults={
                    "results": (
                        "Resultados ficticios de demostración con "
                        "evolución favorable y aspectos por reforzar."
                    ),
                    "observations": (
                        "Registro creado exclusivamente para demostrar "
                        "las funciones de MIL-AL."
                    ),
                    "professional_role": role,
                    "created_by": users[user_key],
                    "updated_by": users[user_key],
                },
            )


def _ensure_interventions(students, users):
    Intervention = _model(
        "students",
        "StudentIntervention",
    )

    for student in students:
        Intervention.objects.update_or_create(
            student=student,
            intervention_date=date(2026, 7, 15),
            professional_role="PSICOLOGO",
            defaults={
                "objectives": (
                    "Fortalecer estrategias de autorregulación "
                    "y comunicación emocional."
                ),
                "observations": (
                    "Intervención ficticia para demostración funcional."
                ),
                "created_by": users["psicologo"],
                "updated_by": users["psicologo"],
            },
        )

        Intervention.objects.update_or_create(
            student=student,
            intervention_date=date(2026, 8, 15),
            professional_role="TERAPEUTA",
            defaults={
                "objectives": (
                    "Mejorar autonomía y seguimiento de instrucciones."
                ),
                "observations": (
                    "Intervención terapéutica ficticia de demostración."
                ),
                "created_by": users["terapeuta"],
                "updated_by": users["terapeuta"],
            },
        )


def _ensure_plans_and_followups(students, users):
    Plan = _model(
        "students",
        "StudentInterventionPlan",
    )
    FollowUp = _model(
        "students",
        "StudentInterventionFollowUp",
    )

    plans = {}

    for student in students:
        psych_plan, _ = Plan.objects.update_or_create(
            student=student,
            professional_role="PSICOLOGO",
            estimated_start_date=date(2026, 8, 1),
            defaults={
                "objectives": (
                    "Consolidar estrategias de regulación emocional "
                    "y adaptación escolar."
                ),
                "estimated_end_date": date(2026, 10, 1),
                "responsible": users["psicologo"],
                "responsible_role": "PSICOLOGO",
                "status": "IN_PROGRESS",
                "created_by": users["psicologo"],
                "updated_by": users["psicologo"],
            },
        )

        therapy_plan, _ = Plan.objects.update_or_create(
            student=student,
            professional_role="TERAPEUTA",
            estimated_start_date=date(2026, 9, 1),
            defaults={
                "objectives": (
                    "Desarrollar autonomía funcional mediante "
                    "actividades estructuradas."
                ),
                "estimated_end_date": date(2026, 12, 15),
                "responsible": users["terapeuta"],
                "responsible_role": "TERAPEUTA",
                "status": "PLANNED",
                "created_by": users["terapeuta"],
                "updated_by": users["terapeuta"],
            },
        )

        plans[(student.pk, "PSICOLOGO")] = psych_plan
        plans[(student.pk, "TERAPEUTA")] = therapy_plan

        for plan, creator, role in (
            (psych_plan, users["psicologo"], "PSICOLOGO"),
            (therapy_plan, users["terapeuta"], "TERAPEUTA"),
        ):
            for index, followup_date in enumerate(
                (
                    plan.estimated_start_date + timedelta(days=14),
                    plan.estimated_start_date + timedelta(days=35),
                ),
                start=1,
            ):
                FollowUp.objects.update_or_create(
                    intervention_plan=plan,
                    followup_date=followup_date,
                    defaults={
                        "progress": (
                            f"Seguimiento {index}: avance gradual "
                            f"en objetivos del área {role.lower()}."
                        ),
                        "results": (
                            "Se documentan avances observables "
                            "y aspectos pendientes de consolidar."
                        ),
                        "observations": (
                            "Información ficticia para demostración."
                        ),
                        "status": (
                            "COMPLETED"
                            if index == 1
                            else "IN_PROGRESS"
                        ),
                        "created_by": creator,
                    },
                )

    return plans


def _ensure_alerts(students, users, plans):
    Alert = _model("alerts", "Alert")
    AlertEvent = _model("alerts", "AlertEvent")

    first_student = students[0]
    overdue_plan = plans[(first_student.pk, "PSICOLOGO")]

    overdue_alert, _ = Alert.objects.update_or_create(
        condition="INTERVENTION_OVERDUE",
        intervention_plan=overdue_plan,
        defaults={
            "student": first_student,
            "assigned_to": users["psicologo"],
            "assigned_role": "PSICOLOGO",
            "reason": (
                "Plan de demostración con fecha estimada de cierre "
                "vencida y seguimiento pendiente."
            ),
            "status": "OPEN",
            "reviewed_by": None,
            "reviewed_at": None,
            "resolved_by": None,
            "resolved_at": None,
        },
    )

    AlertEvent.objects.update_or_create(
        alert=overdue_alert,
        event_type="CREATED",
        defaults={
            "from_status": None,
            "to_status": "OPEN",
            "performed_by": users["psicologo"],
            "note": "Alerta ficticia generada para demostración.",
        },
    )

    second_student = students[1]
    delayed_plan = plans[(second_student.pk, "TERAPEUTA")]

    delayed_alert, _ = Alert.objects.update_or_create(
        condition="INTERVENTION_START_DELAYED",
        intervention_plan=delayed_plan,
        defaults={
            "student": second_student,
            "assigned_to": users["terapeuta"],
            "assigned_role": "TERAPEUTA",
            "reason": (
                "Plan de demostración cuya fecha estimada de inicio "
                "ya transcurrió."
            ),
            "status": "REVIEWED",
            "reviewed_by": users["terapeuta"],
            "reviewed_at": timezone.now(),
            "resolved_by": None,
            "resolved_at": None,
        },
    )

    AlertEvent.objects.update_or_create(
        alert=delayed_alert,
        event_type="CREATED",
        defaults={
            "from_status": None,
            "to_status": "OPEN",
            "performed_by": users["terapeuta"],
            "note": "Alerta ficticia creada para demostración.",
        },
    )

    AlertEvent.objects.update_or_create(
        alert=delayed_alert,
        event_type="REVIEWED",
        defaults={
            "from_status": "OPEN",
            "to_status": "REVIEWED",
            "performed_by": users["terapeuta"],
            "note": "Alerta revisada dentro del escenario demo.",
        },
    )


def _ensure_documents(students, users):
    StudentDocument = _model(
        "students",
        "StudentDocument",
    )

    for student in students:
        payload = (
            "MIL-AL\n"
            "Documento ficticio de demostración.\n"
            f"Estudiante: {student.institutional_code}\n"
            "No contiene información personal real.\n"
        ).encode("utf-8")

        sha256 = hashlib.sha256(payload).hexdigest()

        existing = StudentDocument.objects.filter(
            student=student,
            sha256=sha256,
            is_active=True,
        ).first()

        if existing:
            continue

        filename = (
            f"{student.institutional_code.lower()}-"
            "documento-demo.txt"
        )

        document = StudentDocument(
            student=student,
            document_type="ACADEMICO",
            document_type_detail="",
            original_filename=filename,
            mime_type="text/plain",
            size_bytes=len(payload),
            sha256=sha256,
            description=(
                "Documento ficticio creado por seed_demo_data."
            ),
            is_active=True,
            deactivated_at=None,
            created_by=users["admin"],
            updated_by=users["admin"],
        )

        try:
            document.file.save(
                filename,
                ContentFile(payload),
                save=False,
            )
            document.save()
        except Exception:
            if document.file and document.file.name:
                document.file.storage.delete(document.file.name)
            raise


def seed_demo_data(password: str):
    with transaction.atomic():
        users = _ensure_users(password)
        students = _ensure_students()

        _ensure_assignments(students, users)
        _ensure_family(students, users)
        _ensure_academic_followups(students, users)
        _ensure_psychological_followups(students, users)
        _ensure_therapy_followups(students, users)
        _ensure_evaluations(students, users)
        _ensure_interventions(students, users)

        plans = _ensure_plans_and_followups(
            students,
            users,
        )

        _ensure_alerts(
            students,
            users,
            plans,
        )

    # Los archivos se crean después de confirmar los datos SQL.
    # Así, una falla del almacenamiento no revierte ni deja
    # inconsistente toda la creación relacional.
    _ensure_documents(students, users)

    return {
        "users": len(users),
        "students": len(students),
    }

PROTECTED_USERNAMES = {
    "MIL-AL",
}


def get_demo_counts():
    User = _model("users", "User")
    Student = _model("students", "Student")
    Assignment = _model(
        "students",
        "StudentProfessionalAssignment",
    )
    FamilyMember = _model(
        "students",
        "StudentFamilyMember",
    )
    StudentDocument = _model(
        "students",
        "StudentDocument",
    )
    Intervention = _model(
        "students",
        "StudentIntervention",
    )
    Plan = _model(
        "students",
        "StudentInterventionPlan",
    )
    PlanFollowUp = _model(
        "students",
        "StudentInterventionFollowUp",
    )
    AcademicFollowUp = _model(
        "academic",
        "AcademicFollowUp",
    )
    PsychologicalFollowUp = _model(
        "psychology",
        "PsychologicalFollowUp",
    )
    TherapyFollowUp = _model(
        "therapy",
        "TherapyFollowUp",
    )
    Evaluation = _model(
        "evaluations",
        "Evaluation",
    )
    StudentReport = _model(
        "reports",
        "StudentReport",
    )
    AIInsight = _model(
        "ai_support",
        "AIInsight",
    )
    Alert = _model("alerts", "Alert")
    AlertEvent = _model("alerts", "AlertEvent")

    students = Student.objects.filter(
        institutional_code__startswith=DEMO_STUDENT_PREFIX
    )
    student_ids = list(
        students.values_list("id", flat=True)
    )

    plans = Plan.objects.filter(
        student_id__in=student_ids
    )
    alerts = Alert.objects.filter(
        student_id__in=student_ids
    )

    return {
        "users": User.objects.filter(
            username__startswith=DEMO_USER_PREFIX
        ).count(),
        "students": students.count(),
        "assignments": Assignment.objects.filter(
            student_id__in=student_ids
        ).count(),
        "family_members": FamilyMember.objects.filter(
            student_id__in=student_ids
        ).count(),
        "documents": StudentDocument.objects.filter(
            student_id__in=student_ids
        ).count(),
        "interventions": Intervention.objects.filter(
            student_id__in=student_ids
        ).count(),
        "plans": plans.count(),
        "plan_followups": PlanFollowUp.objects.filter(
            intervention_plan__in=plans
        ).count(),
        "academic_followups": AcademicFollowUp.objects.filter(
            student_id__in=student_ids
        ).count(),
        "psychological_followups": (
            PsychologicalFollowUp.objects.filter(
                student_id__in=student_ids
            ).count()
        ),
        "therapy_followups": TherapyFollowUp.objects.filter(
            student_id__in=student_ids
        ).count(),
        "evaluations": Evaluation.objects.filter(
            student_id__in=student_ids
        ).count(),
        "reports": StudentReport.objects.filter(
            student_id__in=student_ids
        ).count(),
        "ai_insights": AIInsight.objects.filter(
            student_id__in=student_ids
        ).count(),
        "alerts": alerts.count(),
        "alert_events": AlertEvent.objects.filter(
            alert__in=alerts
        ).count(),
    }


def _assert_demo_users_safe_to_delete(user_ids):
    if not user_ids:
        return

    checks = [
        (
            _model(
                "students",
                "StudentProfessionalAssignment",
            ),
            Q(professional_id__in=user_ids)
            | Q(assigned_by_id__in=user_ids),
        ),
        (
            _model(
                "students",
                "StudentFamilyMember",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "students",
                "StudentDocument",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "students",
                "StudentIntervention",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "students",
                "StudentInterventionPlan",
            ),
            Q(responsible_id__in=user_ids)
            | Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "students",
                "StudentInterventionFollowUp",
            ),
            Q(created_by_id__in=user_ids),
        ),
        (
            _model(
                "academic",
                "AcademicFollowUp",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "psychology",
                "PsychologicalFollowUp",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "therapy",
                "TherapyFollowUp",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "evaluations",
                "Evaluation",
            ),
            Q(created_by_id__in=user_ids)
            | Q(updated_by_id__in=user_ids),
        ),
        (
            _model(
                "reports",
                "StudentReport",
            ),
            Q(generated_by_id__in=user_ids),
        ),
        (
            _model(
                "ai_support",
                "AIInsight",
            ),
            Q(generated_by_id__in=user_ids)
            | Q(reviewed_by_id__in=user_ids),
        ),
        (
            _model(
                "alerts",
                "Alert",
            ),
            Q(assigned_to_id__in=user_ids)
            | Q(reviewed_by_id__in=user_ids)
            | Q(resolved_by_id__in=user_ids),
        ),
        (
            _model(
                "alerts",
                "AlertEvent",
            ),
            Q(performed_by_id__in=user_ids),
        ),
    ]

    remaining = []

    for model, condition in checks:
        count = model.objects.filter(condition).count()

        if count:
            remaining.append(
                f"{model._meta.label}: {count}"
            )

    if remaining:
        raise RuntimeError(
            "No se eliminarán los usuarios demo porque "
            "todavía existen registros que los referencian: "
            + ", ".join(remaining)
        )


def reset_demo_data():
    User = _model("users", "User")
    Student = _model("students", "Student")
    Assignment = _model(
        "students",
        "StudentProfessionalAssignment",
    )
    FamilyMember = _model(
        "students",
        "StudentFamilyMember",
    )
    StudentDocument = _model(
        "students",
        "StudentDocument",
    )
    Intervention = _model(
        "students",
        "StudentIntervention",
    )
    Plan = _model(
        "students",
        "StudentInterventionPlan",
    )
    PlanFollowUp = _model(
        "students",
        "StudentInterventionFollowUp",
    )
    AcademicFollowUp = _model(
        "academic",
        "AcademicFollowUp",
    )
    PsychologicalFollowUp = _model(
        "psychology",
        "PsychologicalFollowUp",
    )
    TherapyFollowUp = _model(
        "therapy",
        "TherapyFollowUp",
    )
    Evaluation = _model(
        "evaluations",
        "Evaluation",
    )
    StudentReport = _model(
        "reports",
        "StudentReport",
    )
    AIInsight = _model(
        "ai_support",
        "AIInsight",
    )
    Alert = _model("alerts", "Alert")
    AlertEvent = _model("alerts", "AlertEvent")

    demo_users = User.objects.filter(
        username__startswith=DEMO_USER_PREFIX
    )

    protected = demo_users.filter(
        username__in=PROTECTED_USERNAMES
    )

    if protected.exists():
        raise RuntimeError(
            "Protección activada: un usuario reservado "
            "coincidió con el conjunto demo."
        )

    demo_user_ids = list(
        demo_users.values_list("id", flat=True)
    )

    demo_students = Student.objects.filter(
        institutional_code__startswith=DEMO_STUDENT_PREFIX
    )

    student_ids = list(
        demo_students.values_list("id", flat=True)
    )

    documents = StudentDocument.objects.filter(
        student_id__in=student_ids
    )

    blob_files = []

    for document in documents:
        if document.file and document.file.name:
            blob_files.append(
                (
                    document.file.name,
                    document.file.storage,
                )
            )

    deleted_counts = get_demo_counts()

    with transaction.atomic():
        alerts = Alert.objects.filter(
            student_id__in=student_ids
        )
        alert_ids = list(
            alerts.values_list("id", flat=True)
        )

        plans = Plan.objects.filter(
            student_id__in=student_ids
        )
        plan_ids = list(
            plans.values_list("id", flat=True)
        )

        AlertEvent.objects.filter(
            alert_id__in=alert_ids
        ).delete()

        alerts.delete()

        AIInsight.objects.filter(
            student_id__in=student_ids
        ).delete()

        StudentReport.objects.filter(
            student_id__in=student_ids
        ).delete()

        PlanFollowUp.objects.filter(
            intervention_plan_id__in=plan_ids
        ).delete()

        Evaluation.objects.filter(
            student_id__in=student_ids
        ).delete()

        TherapyFollowUp.objects.filter(
            student_id__in=student_ids
        ).delete()

        PsychologicalFollowUp.objects.filter(
            student_id__in=student_ids
        ).delete()

        AcademicFollowUp.objects.filter(
            student_id__in=student_ids
        ).delete()

        Intervention.objects.filter(
            student_id__in=student_ids
        ).delete()

        documents.delete()

        FamilyMember.objects.filter(
            student_id__in=student_ids
        ).delete()

        Assignment.objects.filter(
            student_id__in=student_ids
        ).delete()

        plans.delete()

        demo_students.delete()

        _assert_demo_users_safe_to_delete(
            demo_user_ids
        )

        demo_users.delete()

    blob_errors = []

    seen_names = set()

    for name, storage in blob_files:
        if name in seen_names:
            continue

        seen_names.add(name)

        try:
            if storage.exists(name):
                storage.delete(name)
        except Exception as exc:
            blob_errors.append(
                f"{name}: {exc}"
            )

    return {
        "deleted": deleted_counts,
        "blob_errors": blob_errors,
    }