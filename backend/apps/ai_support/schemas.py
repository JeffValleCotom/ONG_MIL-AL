ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "trends": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                    },
                    "observation": {
                        "type": "string",
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "area",
                    "observation",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        },
        "progress": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                    },
                    "observation": {
                        "type": "string",
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "area",
                    "observation",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        },
        "attention_points": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                    },
                    "observation": {
                        "type": "string",
                    },
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "area",
                    "observation",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "summary",
        "trends",
        "progress",
        "attention_points",
    ],
    "additionalProperties": False,
}


FOLLOWUP_SUGGESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "rationale": {
                        "type": "string",
                    },
                    "related_data": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "title",
                    "rationale",
                    "related_data",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "summary",
        "suggestions",
    ],
    "additionalProperties": False,
}


INTERVENTION_RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                    },
                    "action": {
                        "type": "string",
                    },
                    "rationale": {
                        "type": "string",
                    },
                    "related_data": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                    "cautions": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "objective",
                    "action",
                    "rationale",
                    "related_data",
                    "cautions",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "summary",
        "recommendations",
    ],
    "additionalProperties": False,
}


REPORT_SUGGESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "suggested_sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                    },
                    "draft_text": {
                        "type": "string",
                    },
                    "rationale": {
                        "type": "string",
                    },
                },
                "required": [
                    "section",
                    "draft_text",
                    "rationale",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "summary",
        "suggested_sections",
    ],
    "additionalProperties": False,
}
