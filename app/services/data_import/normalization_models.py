from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ColumnMapping:
    source_column: str
    target_field: Optional[str]
    confidence: float
    method: str
    reason: str = ""


@dataclass
class MissingField:
    field: str
    required: bool
    reason: str
    can_infer: bool = False


@dataclass
class NormalizationResult:
    status: str
    mappings: List[ColumnMapping] = field(default_factory=list)
    missing_fields: List[MissingField] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_rows: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def requires_user_input(self) -> bool:
        return any(
            item.required
            for item in self.missing_fields
        )
