"""
PIP Smart Import Agent

MVP architecture:

Deterministic Mapper
        |
        | candidate mapping
        v
Semantic Validator Agent
        |
        +--> ACCEPT
        |
        +--> ASK USER

The Agent validates an existing candidate.
It does not freely invent mappings.
"""


import json
import re
from typing import Any

from app.services.ai.ollama_client import generate


def _extract_json_object(text):
    """
    Extract a JSON object from an Ollama response.

    Supports:
      - raw JSON
      - ```json ... ```
      - ``` ... ```
      - surrounding explanatory text

    Returns:
      dict | None
    """

    if not text:
        return None

    text = str(text).strip()

    # Markdown fenced JSON
    if "```" in text:

        blocks = text.split("```")

        for block in blocks:

            candidate = block.strip()

            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()

            if candidate.startswith("{") and candidate.endswith("}"):

                try:
                    parsed = json.loads(candidate)

                    if isinstance(parsed, dict):
                        return parsed

                except Exception:
                    pass

    # Raw JSON
    try:

        parsed = json.loads(text)

        if isinstance(parsed, dict):
            return parsed

    except Exception:
        pass

    # Find first JSON object inside surrounding text
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:

        candidate = text[start:end + 1]

        try:

            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except Exception:
            pass

    return None


def _validate_agent_decision(result, allowed_targets):
    """
    Strict Smart Import Agent contract.

    The LLM may suggest a target, but the target must exist
    in the canonical target list supplied by the normalizer.
    """

    if not isinstance(result, dict):
        return None

    target = result.get("target")
    confidence = result.get("confidence")

    if target not in allowed_targets:
        return None

    try:
        confidence = float(confidence)
    except Exception:
        return None

    if confidence < 0 or confidence > 1:
        return None

    return {
        "target": target,
        "confidence": confidence,
    }



ALLOWED_TARGETS = {
    "activity_code",
    "activity_name",
    "wbs_id",
    "duration_days",
    "progress_percent",
    "status",
    "start_date",
    "finish_date",
    "responsible_party",
}


def _extract_json(text: str) -> dict[str, Any] | None:

    if not text:
        return None

    text = text.strip()

    # Direct JSON
    try:

        data = json.loads(text)

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    # Markdown JSON
    match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if match:

        try:

            data = json.loads(
                match.group(1)
            )

            if isinstance(data, dict):
                return data

        except Exception:
            pass

    # First JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:

        try:

            data = json.loads(
                text[start:end + 1]
            )

            if isinstance(data, dict):
                return data

        except Exception:
            pass

    return None


def _safe_confidence(value: Any) -> float:

    try:
        value = float(value)
    except Exception:
        return 0.0

    return max(
        0.0,
        min(1.0, value),
    )


def resolve_column_mapping(
    source_column: str,
    candidate_target: str | None = None,
    confidence: float | None = None,
    reason: str | None = None,
    sample_values: list | None = None,
    all_columns: list | None = None,
) -> dict[str, Any]:

    source_column = str(
        source_column or ""
    ).strip()

    candidate_target = (
        str(candidate_target).strip()
        if candidate_target
        else None
    )

    # --------------------------------------------------------
    # HARD SAFETY CHECK
    # --------------------------------------------------------

    if (
        candidate_target
        and candidate_target not in ALLOWED_TARGETS
    ):

        candidate_target = None

    # --------------------------------------------------------
    # STRONG DETERMINISTIC CANDIDATE
    # --------------------------------------------------------


    # --------------------------------------------------------
    # AI SEMANTIC VALIDATION
    # --------------------------------------------------------

    prompt = f"""
You are an EPC project schedule semantic validator.

Source column:
{source_column}

Candidate target:
{candidate_target}

Sample values:
{sample_values}

Available canonical fields:
activity_code, activity_name, wbs_id, duration_days,
progress_percent, status, start_date, finish_date,
responsible_party

Rules:
- If the source clearly identifies who performs or owns the activity, use responsible_party.
- If candidate_target is None, infer the best canonical field from the source name and sample values.
- Do not confuse responsible_party with status.
- Accept only a clear semantic match.
- Do not invent fields.
- Return exactly one JSON object.
- Keep reason very short.

Required JSON:
{{"decision":"accept","target":"responsible_party","confidence":0.95,"reason":"semantic match"}}

If uncertain:
{{"decision":"ask_user","target":null,"confidence":0.0,"reason":"uncertain semantic mapping"}}
"""

    try:

        response = generate(
            prompt,
            timeout=40,
            num_predict=60,
            temperature=0.0,
        )

        parsed_response = _extract_json_object(response)

        # ============================================================
        # COMMITTEE JSON PARSER FIX
        #
        # _extract_json_object() is the canonical tolerant parser.
        # It supports raw JSON, fenced JSON and surrounding text.
        #
        # The previous implementation computed parsed_response but
        # then ignored it and called the older parser again. This could
        # incorrectly classify a valid Ollama response as invalid JSON.
        # ============================================================
        parsed = parsed_response

        if not isinstance(parsed, dict):
            parsed = _extract_json(response)

        if not parsed:

            return {
                "decision": "ask_user",
                "target": None,
                "confidence": 0.0,
                "reason": (
                    "AI response was not valid JSON."
                ),
                "question": (
                    f"ستون '{source_column}' "
                    "مربوط به کدام فیلد پروژه است؟"
                ),
                "ai_status": "invalid_response",
            }

        decision = str(
            parsed.get(
                "decision",
                "ask_user",
            )
        ).strip().lower()

        target = parsed.get("target")

        if target is not None:

            target = str(
                target
            ).strip()

        ai_confidence = _safe_confidence(
            parsed.get(
                "confidence",
                0.0,
            )
        )

        # ----------------------------------------------------
        # DETERMINISTIC SEMANTIC GUARD
        # ----------------------------------------------------
        #
        # qwen2.5:1.5b may correctly identify the target while
        # returning a conservative confidence such as 0.82.
        #
        # For clearly semantic responsibility columns, the
        # deterministic EPC vocabulary is stronger than the
        # model confidence alone.
        #
        # Example:
        # Party Responsible -> responsible_party
        # Contractor        -> responsible_party
        # Engineering Dept  -> responsible_party
        # Construction Team -> responsible_party
        #
        # This guard does NOT allow the AI to invent a target.
        # It only validates the deterministic candidate.

        responsibility_keywords = (
            "responsible",
            "responsibility",
            "contractor",
            "party",
            "owner",
            "discipline",
            "department",
            "team",
            "engineer",
            "vendor",
        )

        source_lower = source_column.lower()

        responsibility_semantic_match = (
            (
                candidate_target == "responsible_party"
                or candidate_target is None
            )
            and any(
                keyword in source_lower
                for keyword in responsibility_keywords
            )
        )

        semantic_inference_allowed = (
            candidate_target is None
            and target == "responsible_party"
            and responsibility_semantic_match
        )

        candidate_validation_passed = (
            candidate_target is not None
            and target == candidate_target
        )

        if (
            decision == "accept"
            and target in ALLOWED_TARGETS
            and (
                candidate_validation_passed
                or semantic_inference_allowed
            )
            and (
                ai_confidence >= 0.90
                or responsibility_semantic_match
            )
        ):

            final_confidence = ai_confidence

            if responsibility_semantic_match:
                final_confidence = max(
                    final_confidence,
                    0.95,
                )

            return {
                "decision": "accept",
                "target": target,
                "confidence": final_confidence,
                "reason": str(
                    parsed.get(
                        "reason",
                        "AI semantic validation passed.",
                    )
                ),
                "question": None,
                "ai_status": "completed",
            }
        # SAFE FALLBACK
        # ----------------------------------------------------

        question = parsed.get(
            "question"
        )

        if not question:

            question = (
                f"ستون '{source_column}' "
                "مربوط به کدام فیلد پروژه است؟"
            )

        return {
            "decision": "ask_user",
            "target": None,
            "confidence": ai_confidence,
            "reason": str(
                parsed.get(
                    "reason",
                    "Candidate mapping requires user confirmation.",
                )
            ),
            "question": str(question),
            "ai_status": "completed",
        }

    except Exception as exc:

        return {
            "decision": "ask_user",
            "target": None,
            "confidence": 0.0,
            "reason": (
                "AI semantic validation failed."
            ),
            "question": (
                f"ستون '{source_column}' "
                "مربوط به کدام فیلد پروژه است؟"
            ),
            "ai_status": "fallback",
            "ai_error": str(exc),
        }


def resolve_normalization_review(
    mappings: list,
    rows: list | None = None,
) -> dict[str, Any]:

    rows = rows or []

    accepted = []
    questions = []

    for mapping in mappings:

        method = str(
            mapping.get(
                "method",
                "",
            )
        ).lower()

        confidence = _safe_confidence(
            mapping.get(
                "confidence",
                0.0,
            )
        )

        # ----------------------------------------------------
        # TRUST DETERMINISTIC HIGH-CONFIDENCE MAPPINGS
        # ----------------------------------------------------

        if (
            method != "fuzzy_review"
            and confidence >= 0.90
        ):

            accepted.append(
                dict(mapping)
            )

            continue

        # ----------------------------------------------------
        # AI VALIDATION
        # ----------------------------------------------------

        source = (
            mapping.get("source")
            or mapping.get("source_column")
            or mapping.get("column")
        )

        target = mapping.get(
            "target"
        )

        if not source:

            questions.append({
                "source": None,
                "question": (
                    "ستون مبهمی شناسایی شده "
                    "ولی نام ستون مشخص نیست."
                ),
            })

            continue

        sample_values = []

        for row in rows[:8]:

            if (
                isinstance(row, dict)
                and source in row
            ):

                sample_values.append(
                    row.get(source)
                )

        result = resolve_column_mapping(
            source_column=str(source),
            candidate_target=target,
            confidence=confidence,
            reason=mapping.get("reason"),
            sample_values=sample_values,
            all_columns=[],
        )

        if result["decision"] == "accept":

            updated = dict(mapping)

            updated["target"] = result[
                "target"
            ]

            updated["confidence"] = result[
                "confidence"
            ]

            updated["method"] = (
                "ai_semantic_validation"
            )

            updated["reason"] = result[
                "reason"
            ]

            accepted.append(
                updated
            )

        else:

            questions.append({
                "source": source,
                "target_candidate": target,
                "confidence": result[
                    "confidence"
                ],
                "reason": result[
                    "reason"
                ],
                "question": result[
                    "question"
                ],
                "ai_status": result.get(
                    "ai_status"
                ),
            })

    return {
        "accepted_mappings": accepted,
        "questions": questions,
        "needs_user_input": (
            len(questions) > 0
        ),
        "ai_resolved": len(
            [
                x
                for x in accepted
                if x.get("method")
                == "ai_semantic_validation"
            ]
        ),
    }






