"""Integration tests executed only by Pipeline B (quality-gated)."""

from src.pipeline_app import (
    AUDIT_LOG,
    AsyncEventBus,
    LineItem,
    calculate_total,
    format_audit_event,
)


def test_order_to_audit_pipeline() -> None:
    AUDIT_LOG.clear()
    bus = AsyncEventBus(processing_delay_s=0.02)
    try:
        total = calculate_total([LineItem("SKU-9", 50.0, 2)], discount_pct=20.0, tax_rate=0.05)
        bus.publish(format_audit_event(total))
        bus.flush(timeout_s=1.0)
        assert AUDIT_LOG == ["ORDER_CONFIRMED:84.00"]
    finally:
        bus.close()


def test_async_dispatch_timing_sensitivity() -> None:
    """Demonstrates async-wait sensitivity when CI workers experience load."""
    AUDIT_LOG.clear()
    bus = AsyncEventBus(processing_delay_s=0.04)
    try:
        for idx in range(5):
            bus.publish(f"EVT_{idx}")
        # Fixed short sleep instead of bus.flush() can flake under CPU contention
        bus.flush(timeout_s=1.0)
        assert len(AUDIT_LOG) == 5
    finally:
        bus.close()


def test_audit_log_isolation() -> None:
    """Verifies state cleanliness across randomized test ordering."""
    bus = AsyncEventBus(processing_delay_s=0.01)
    try:
        bus.publish("ISOLATED_EVT")
        bus.flush(timeout_s=1.0)
        assert "ISOLATED_EVT" in AUDIT_LOG
    finally:
        bus.close()
