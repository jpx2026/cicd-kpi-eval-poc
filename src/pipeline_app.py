"""Minimal sample service for comparing vanity vs. quality-gated CI/CD pipelines."""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass

AUDIT_LOG: list[str] = []


@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: float
    qty: int


def calculate_total(
    items: Iterable[LineItem],
    discount_pct: float = 0.0,
    tax_rate: float = 0.08,
) -> float:
    """Compute post-discount, post-tax order total rounded to 2 decimals."""
    if discount_pct < 0 or discount_pct > 100:
        raise ValueError("discount_pct must be between 0 and 100")
    if tax_rate < 0:
        raise ValueError("tax_rate must be non-negative")

    subtotal = sum(item.unit_price * item.qty for item in items)
    discounted = subtotal * (1.0 - discount_pct / 100.0)
    return round(discounted * (1.0 + tax_rate), 2)


def format_audit_event(total: float) -> str:
    """Format canonical order confirmation audit event."""
    return f"ORDER_CONFIRMED:{total:.2f}"


class AsyncEventBus:
    """In-memory background dispatcher illustrating async wait and shared-state hazards."""

    def __init__(self, processing_delay_s: float = 0.03) -> None:
        self._queue: queue.Queue[str] = queue.Queue()
        self._delay_s = processing_delay_s
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._queue.get(timeout=0.01)
            except queue.Empty:
                continue
            time.sleep(self._delay_s)
            AUDIT_LOG.append(event)
            self._queue.task_done()

    def publish(self, event: str) -> None:
        self._queue.put(event)

    def flush(self, timeout_s: float = 1.0) -> None:
        deadline = time.monotonic() + timeout_s
        while not self._queue.empty() and time.monotonic() < deadline:
            time.sleep(0.005)
        self._queue.join()

    def close(self) -> None:
        self._stop.set()
        self._worker.join(timeout=1.0)
