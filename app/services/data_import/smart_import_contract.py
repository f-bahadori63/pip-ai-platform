"""
PIP Smart Import Integration Contract

This module provides the explicit boundary between
the deterministic normalizer and the Smart Import Agent.

It does not perform database imports.
"""

from app.services.ai.smart_import_agent import (
    resolve_normalization_review,
)


def resolve_normalization_with_ai(
    normalization_result: dict,
) -> dict:

    mappings = normalization_result.get(
        "mappings",
        []
    )

    rows = normalization_result.get(
        "normalized_rows",
        []
    )

    result = resolve_normalization_review(
        mappings=mappings,
        rows=rows,
    )

    output = dict(normalization_result)

    output["ai_resolution"] = result

    if result["needs_user_input"]:

        output["status"] = "needs_review"
        output["needs_review"] = True
        output["needs_user_input"] = True

        output["user_questions"] = result[
            "questions"
        ]

        return output

    # Replace only the mappings that AI safely resolved.
    output["mappings"] = result[
        "accepted_mappings"
    ]

    output["needs_review"] = False
    output["needs_user_input"] = False
    output["status"] = "ready"

    return output
