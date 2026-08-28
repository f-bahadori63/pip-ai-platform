"""Regression tests for the EVM engine (pure functions, no database)."""

import pytest

from app.services.evm_engine import _weighted_mix, compute_evm


def _activity(
    planned: float | None,
    actual: float | None,
    duration: int | None,
) -> dict:
    return {
        "planned_progress": planned,
        "actual_progress": actual,
        "duration_days": duration,
    }


def test_weighted_mix_balanced():
    schedule = [
        _activity(50.0, 30.0, 10),
        _activity(50.0, 70.0, 10),
    ]

    planned, actual = _weighted_mix(schedule)

    assert planned == 50.0
    assert actual == 50.0


def test_weighted_mix_prefers_duration():
    schedule = [
        _activity(0.0, 0.0, 90),
        _activity(100.0, 100.0, 10),
    ]

    planned, actual = _weighted_mix(schedule)

    assert planned == 10.0
    assert actual == 10.0


def test_weighted_mix_no_schedule():
    planned, actual = _weighted_mix([])

    assert planned is None
    assert actual is None


def test_weighted_mix_missing_values_fill_from_counterpart():
    schedule = [
        _activity(40.0, None, 10),
        _activity(None, 60.0, 10),
    ]

    planned, actual = _weighted_mix(schedule)

    # row 1 contributes planned=40/actual=40, row 2 planned=60/actual=60
    assert planned == 50.0
    assert actual == 50.0


def test_evm_known_values():
    evm = compute_evm(
        schedule_data=[
            _activity(50.0, 30.0, 10),
            _activity(50.0, 70.0, 10),
        ],
        budget=1000.0,
        actual_cost=400.0,
    )

    assert evm["bac"] == 1000.0
    assert evm["pv"] == 500.0
    assert evm["ev"] == 500.0
    assert evm["ac"] == 400.0
    assert evm["sv"] == 0.0
    assert evm["spi"] == 1.0
    assert evm["cv"] == 100.0
    assert evm["cpi"] == 1.25
    assert evm["eac"] == 800.0
    assert evm["etc"] == 400.0
    assert evm["vac"] == 200.0
    assert evm["tcpi"] == pytest.approx(0.8333, abs=0.001)
    assert evm["status"] == "GREEN"


def test_evm_behind_schedule_red():
    evm = compute_evm(
        schedule_data=[
            _activity(80.0, 40.0, 10),
        ],
        budget=1000.0,
        actual_cost=600.0,
    )

    assert evm["spi"] == pytest.approx(0.5, abs=0.001)
    assert evm["cpi"] == pytest.approx(0.6667, abs=0.001)
    assert evm["status"] == "RED"


def test_evm_guard_zero_planned():
    evm = compute_evm(
        schedule_data=[
            _activity(0.0, 30.0, 10),
        ],
        budget=1000.0,
        actual_cost=200.0,
    )

    assert evm["pv"] == 0.0
    assert evm["spi"] is None
    assert evm["status"] == "NO_BASELINE"


def test_evm_guard_zero_actual_cost():
    evm = compute_evm(
        schedule_data=[
            _activity(60.0, 50.0, 10),
        ],
        budget=1000.0,
        actual_cost=0.0,
    )

    assert evm["cpi"] is None
    assert evm["eac"] is None
    assert evm["cv"] == 500.0


def test_evm_no_schedule():
    evm = compute_evm([], budget=1000.0)

    assert evm["status"] == "no_schedule"


def test_evm_no_budget():
    evm = compute_evm(
        schedule_data=[
            _activity(50.0, 50.0, 10),
        ],
        budget=None,
    )

    assert evm["status"] == "no_budget"
    assert evm["bac"] is None
