from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..config import settings

logger = logging.getLogger(__name__)

_PROGRESS_BLOCK_PATTERN = re.compile(
    r"\[progress\|(?P<task>[^|\]]+)\|(?P<value>\d{1,3})(?:\|(?P<note>[^\]]+))?\]",
    flags=re.IGNORECASE,
)


@dataclass(slots=True)
class ProgressAnnotation:
    task_name: str
    progress: int
    note: str | None = None


def _clamp_progress(value: int) -> int:
    return max(0, min(100, value))


def extract_progress_annotations(message: str) -> List[ProgressAnnotation]:
    annotations: List[ProgressAnnotation] = []
    for match in _PROGRESS_BLOCK_PATTERN.finditer(message or ""):
        task_name = match.group("task").strip()
        if not task_name:
            continue
        raw_value = match.group("value")
        try:
            progress_value = _clamp_progress(int(raw_value))
        except ValueError:
            logger.debug("Unable to parse progress value '%s'", raw_value)
            continue
        note = match.group("note")
        annotations.append(
            ProgressAnnotation(
                task_name=task_name,
                progress=progress_value,
                note=note.strip() if note else None,
            )
        )
    return annotations


def get_or_create_task(db: Session, task_name: str) -> models.Task:
    task = db.execute(
        select(models.Task).where(models.Task.name == task_name)
    ).scalar_one_or_none()
    if task is None:
        task = models.Task(name=task_name, progress=0)
        db.add(task)
        db.flush()
    return task


def apply_progress_event(
    db: Session,
    *,
    task: models.Task,
    progress_value: int,
    source: str,
    note: str | None = None,
) -> models.TaskEvent:
    progress_value = _clamp_progress(progress_value)
    task.progress = progress_value
    event = models.TaskEvent(task_id=task.id, progress=progress_value, source=source, note=note)
    db.add(event)
    db.flush()
    return event


def advance_next_task(db: Session, step: int) -> models.Task | None:
    task = db.execute(
        select(models.Task).where(models.Task.progress < 100).order_by(models.Task.updated_at)
    ).scalar_one_or_none()
    if task is None:
        return None
    bounded_step = max(1, step)
    increment = bounded_step if task.progress <= 100 - bounded_step else max(1, 100 - task.progress)
    task.progress = min(100, task.progress + increment)
    db.add(task)
    return task


def get_recent_events(db: Session, limit: int) -> List[models.TaskEvent]:
    return (
        db.execute(
            select(models.TaskEvent)
            .order_by(models.TaskEvent.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )


def calculate_overall_progress(tasks: Iterable[models.Task]) -> float:
    tasks_list = list(tasks)
    if not tasks_list:
        return 0.0
    total = sum(task.progress for task in tasks_list)
    return round(total / len(tasks_list), 2)


def reset_progress_from_config(db: Session) -> List[models.Task]:
    db.query(models.TaskEvent).delete()
    db.query(models.Task).delete()

    seeded_tasks: List[models.Task] = []
    for entry in getattr(settings, "progress", []):
        task = models.Task(
            name=entry["name"],
            progress=_clamp_progress(int(entry.get("progress", 0))),
            description=entry.get("description"),
        )
        db.add(task)
        seeded_tasks.append(task)
    db.flush()
    return seeded_tasks
