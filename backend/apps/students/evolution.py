FOLLOWUP_RECORD_TYPES = {
    "ACADEMIC_FOLLOWUP",
    "PSYCHOLOGICAL_FOLLOWUP",
    "THERAPY_FOLLOWUP",
}


EVIDENCE_FIELDS_BY_TYPE = {
    "ACADEMIC_FOLLOWUP": (
        "strengths",
        "areas_for_improvement",
        "observations",
        "recommendations",
    ),
    "PSYCHOLOGICAL_FOLLOWUP": (
        "observations",
        "emotional_behavioral_notes",
        "recommendations",
    ),
    "THERAPY_FOLLOWUP": (
        "progress_notes",
        "objectives",
        "activities",
        "recommendations",
    ),
    "EVALUATION": (
        "results",
        "observations",
    ),
}


def _build_evidence(item):
    fields = EVIDENCE_FIELDS_BY_TYPE.get(
        item["record_type"],
        (),
    )

    evidence = []

    for field in fields:
        value = item["details"].get(field)

        if value is None:
            continue

        value = str(value).strip()

        if not value:
            continue

        evidence.append(
            {
                "field": field,
                "value": value,
            }
        )

    return evidence


def _build_period_record(item):
    return {
        "record_id": item["record_id"],
        "student_id": item["student_id"],
        "record_type": item["record_type"],
        "area": item["area"],
        "date": item["date"],
        "title": item["title"],
        "evidence": _build_evidence(item),
    }


def build_student_evolution(history_items):
    if not history_items:
        return {
            "summary": {
                "total_records": 0,
                "followup_count": 0,
                "evaluation_count": 0,
                "period_count": 0,
                "first_record_date": None,
                "latest_record_date": None,
            },
            "periods": [],
        }

    periods_by_key = {}

    followup_count = 0
    evaluation_count = 0

    for item in history_items:
        record_date = item["date"]
        period_key = record_date.strftime("%Y-%m")

        if item["record_type"] in FOLLOWUP_RECORD_TYPES:
            followup_count += 1
        elif item["record_type"] == "EVALUATION":
            evaluation_count += 1

        if period_key not in periods_by_key:
            periods_by_key[period_key] = {
                "period": period_key,
                "total_records": 0,
                "followup_count": 0,
                "evaluation_count": 0,
                "areas": set(),
                "records": [],
            }

        period = periods_by_key[period_key]

        period["total_records"] += 1
        period["areas"].add(item["area"])

        if item["record_type"] in FOLLOWUP_RECORD_TYPES:
            period["followup_count"] += 1
        elif item["record_type"] == "EVALUATION":
            period["evaluation_count"] += 1

        period["records"].append(
            _build_period_record(item)
        )

    periods = []

    for period in periods_by_key.values():
        period["areas"] = sorted(
            period["areas"]
        )
        periods.append(period)

    return {
        "summary": {
            "total_records": len(history_items),
            "followup_count": followup_count,
            "evaluation_count": evaluation_count,
            "period_count": len(periods),
            "first_record_date": (
                history_items[-1]["date"]
            ),
            "latest_record_date": (
                history_items[0]["date"]
            ),
        },
        "periods": periods,
    }
