from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None

    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def profile_excel(file_path: str | Path) -> dict[str, Any]:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    workbook = pd.ExcelFile(file_path)

    sheets: list[dict[str, Any]] = []

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
        )

        columns = []

        for column in df.columns:
            series = df[column]

            non_null = series.dropna()

            samples = [
                _json_safe(value)
                for value in non_null.head(5).tolist()
            ]

            columns.append(
                {
                    "name": str(column).strip(),
                    "dtype": str(series.dtype),
                    "non_null": int(series.notna().sum()),
                    "null_count": int(series.isna().sum()),
                    "samples": samples,
                }
            )

        sheets.append(
            {
                "name": sheet_name,
                "rows": int(len(df)),
                "columns": columns,
            }
        )

    return {
        "file_name": file_path.name,
        "sheet_count": len(sheets),
        "sheets": sheets,
    }
