from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from threading import Event, Thread
from time import sleep
from typing import Dict, Iterable, Optional

from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal
from .. import models
from . import progress_tracker


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TaskOverride:
    """Configuration for a specific task override."""

    step: int
    note: Optional[str] = None


@dataclass(slots=True)
class TelemetryConfig:
    """Runtime configuration for the telemetry agent."""

    enabled: bool = False
    interval_seconds: float = 45.0
    max_tasks_per_cycle: int = 1
    source: str = "auto-telemetry"
    default_step: int = 5
    note_template: str = "Automated telemetry pulse for {task} @ {timestamp}"
    task_overrides: Dict[str, TaskOverride] | None = None

    @classmethod
    def from_settings(cls) -> "TelemetryConfig":
        config = settings.get("telemetry_agent", default=None)
        if not config:
            return cls(enabled=False)

        overrides: Dict[str, TaskOverride] = {}
        for name, override in (config.get("task_overrides", {}) or {}).items():
            try:
                overrides[name] = TaskOverride(
                    step=max(1, int(override.get("step", config.get("default_step", 5)))),
                    note=override.get("note"),
                )
            except Exception as exc:  # noqa: BLE001 - defensive parsing
                logger.warning("Invalid telemetry override for '%s': %s", name, exc)

        return cls(
            enabled=bool(config.get("enabled", False)),
            interval_seconds=float(config.get("interval_seconds", 45)),
            max_tasks_per_cycle=max(1, int(config.get("max_tasks_per_cycle", 1))),
            source=str(config.get("source", "auto-telemetry")),
            default_step=max(1, int(config.get("default_step", 5))),
            note_template=str(
                config.get(
                    "note_template",
                    "Automated telemetry pulse for {task} @ {timestamp}",
                )
            ),
            task_overrides=overrides or None,
        )


@contextmanager
def _session_scope() -> Iterable[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class TelemetryAgent:
    """Background worker that emits task telemetry at regular intervals."""

    def __init__(self, config: TelemetryConfig) -> None:
        self._config = config
        self._stop_event = Event()
        self._thread: Thread | None = None

    @property
    def is_enabled(self) -> bool:
        return self._config.enabled

    def start(self) -> None:
        if not self.is_enabled:
            logger.info("Telemetry agent is disabled by configuration.")
            return
        if self._thread and self._thread.is_alive():
            return

        logger.info(
            "Starting telemetry agent (interval=%ss, max_tasks_per_cycle=%s).",
            self._config.interval_seconds,
            self._config.max_tasks_per_cycle,
        )
        self._thread = Thread(target=self._run, name="telemetry-agent", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.info("Stopping telemetry agent...")
            self._stop_event.set()
            self._thread.join(timeout=self._config.interval_seconds + 1)
        self._thread = None
        self._stop_event.clear()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception as exc:  # noqa: BLE001 - background safety net
                logger.exception("Telemetry agent tick failed: %s", exc)
            sleep(self._config.interval_seconds)

    def _tick(self) -> None:
        tasks_processed = 0
        with _session_scope() as session:
            tasks = (
                session.query(models.Task)
                .filter(models.Task.progress < 100)
                .order_by(models.Task.updated_at)
                .all()
            )

            for task in tasks:
                if tasks_processed >= self._config.max_tasks_per_cycle:
                    break

                override = (self._config.task_overrides or {}).get(task.name)
                step = override.step if override else self._config.default_step
                next_progress = min(100, task.progress + step)
                if next_progress <= task.progress:
                    continue

                note = None
                if override and override.note:
                    note = override.note
                else:
                    note = self._config.note_template.format(
                        task=task.name,
                        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
                        progress=next_progress,
                    )

                progress_tracker.apply_progress_event(
                    session,
                    task=task,
                    progress_value=next_progress,
                    source=self._config.source,
                    note=note,
                )
                logger.debug(
                    "Telemetry agent advanced '%s' to %s%% via source '%s'",
                    task.name,
                    next_progress,
                    self._config.source,
                )
                tasks_processed += 1

        if tasks_processed == 0:
            logger.debug("Telemetry agent tick completed with no tasks updated.")


def create_agent_from_config() -> TelemetryAgent:
    return TelemetryAgent(TelemetryConfig.from_settings())

