from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from automation.logging.logger import logger
from automation.logging.step_logger import record_step_log


@dataclass(frozen=True)
class StepMetric:
    check_label: str
    duration_seconds: float
    threshold_seconds: float
    forced_status: str | None = None

    @property
    def passed(self) -> bool:
        if self.forced_status == "FAIL":
            return False
        return self.duration_seconds <= self.threshold_seconds

    @property
    def status(self) -> str:
        if self.forced_status:
            return self.forced_status
        return "PASS" if self.passed else "FAIL"

    def format_lines(self) -> list[str]:
        return [
            f"Performance Check - {self.check_label} Elapsed Time : {self.duration_seconds:.2f}s",
            f"Threshold    : {self.threshold_seconds:.2f}s",
            f"Status       : {self.status}",
        ]


class StepPerformanceTracker:
    """Measure page-load duration; assert all thresholds after every step is recorded."""

    def __init__(self, threshold_seconds: float | None = None) -> None:
        self.default_threshold_seconds = threshold_seconds or 10.0
        self.metrics: list[StepMetric] = []

    def run_step(
        self,
        check_label: str,
        action: Callable[[], None],
        *,
        threshold_seconds: float | None = None,
    ) -> StepMetric:
        threshold = (
            threshold_seconds
            if threshold_seconds is not None
            else self.default_threshold_seconds
        )

        record_step_log(f"[PERF START] Performance Check - {check_label}")
        logger.info("PERF START: Performance Check - {}", check_label)
        started_at = time.monotonic()

        try:
            action()
        except Exception:
            duration = time.monotonic() - started_at
            self.metrics.append(
                StepMetric(
                    check_label,
                    duration,
                    threshold,
                    forced_status="FAIL",
                )
            )
            raise

        duration = time.monotonic() - started_at
        metric = StepMetric(check_label, duration, threshold)
        self.metrics.append(metric)
        return metric

    def log_summary(self) -> None:
        if not self.metrics:
            return

        record_step_log("=== Performance Summary ===")
        logger.info("=== Performance Summary ===")

        for metric in self.metrics:
            for line in metric.format_lines():
                record_step_log(line)
                logger.info(line)

    def assert_all_within_threshold(self) -> None:
        self.log_summary()
        failed = [metric for metric in self.metrics if not metric.passed]
        if not failed:
            return

        details = "\n".join(
            "\n".join(metric.format_lines()) for metric in failed
        )
        raise AssertionError(
            f"Performance threshold exceeded — {len(failed)} check(s) failed:\n{details}"
        )
