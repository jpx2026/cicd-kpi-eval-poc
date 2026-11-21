"""Fast unit tests executed by both Pipeline A and Pipeline B."""

import pytest

from src.pipeline_app import LineItem, apply_cap, calculate_total


def test_calculate_total_basic() -> None:
    items = [LineItem("SKU-1", 25.0, 2), LineItem("SKU-2", 10.0, 1)]
    assert calculate_total(items, discount_pct=10.0, tax_rate=0.10) == 59.40


def test_calculate_total_zero_discount() -> None:
    items = [LineItem("SKU-3", 19.99, 1)]
    assert calculate_total(items, discount_pct=0.0, tax_rate=0.0) == 19.99


def test_calculate_total_rejects_invalid_discount() -> None:
    with pytest.raises(ValueError):
        calculate_total([LineItem("SKU-1", 10.0, 1)], discount_pct=150.0)


def test_apply_cap() -> None:
    assert apply_cap(650.0, 500.0) == 500.0
