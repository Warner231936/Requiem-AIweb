from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from .. import models
from . import progress_tracker


@dataclass(slots=True)
class TaskAnalyticsResult:
    name: str
    progress: int
    completed: bool
    events_count: int
    last_event_at: Optional[datetime]
    last_event_source: Optional[str]
    last_event_note: Optional[str]
    seconds_to_completion: Optional[float]


@dataclass(slots=True)
class ProgressAnalyticsResult:
    tasks_total: int
    tasks_completed: int
    tasks_in_progress: int
    tasks_not_started: int
    overall_progress: float
    events_total: int
    events_by_source: Dict[str, int]
    last_event_at: Optional[datetime]
    average_completion_seconds: Optional[float]
    per_task: List[TaskAnalyticsResult]


def _group_events_by_task(events: Iterable[models.TaskEvent]) -> Dict[int, List[models.TaskEvent]]:
    grouped: Dict[int, List[models.TaskEvent]] = defaultdict(list)
    for event in events:
        grouped[event.task_id].append(event)
    for collection in grouped.values():
        collection.sort(key=lambda entry: entry.created_at)
    return grouped


def _calculate_seconds_to_completion(task: models.Task, events: List[models.TaskEvent]) -> Optional[float]:
    if not events:
        if task.progress >= 100:
            return 0.0
        return None

    completion_event = next((event for event in events if event.progress >= 100), None)
    if completion_event is None:
        return None

    start_time = events[0].created_at
    return (completion_event.created_at - start_time).total_seconds()


def _build_task_analytics(task: models.Task, events: List[models.TaskEvent]) -> TaskAnalyticsResult:
    seconds_to_completion = _calculate_seconds_to_completion(task, events)
    last_event = events[-1] if events else None
    return TaskAnalyticsResult(
        name=task.name,
        progress=task.progress,
        completed=task.progress >= 100,
        events_count=len(events),
        last_event_at=last_event.created_at if last_event else None,
        last_event_source=last_event.source if last_event else None,
        last_event_note=last_event.note if last_event else None,
        seconds_to_completion=seconds_to_completion,
    )


def compute_progress_analytics(db: Session) -> ProgressAnalyticsResult:
    tasks: List[models.Task] = db.query(models.Task).order_by(models.Task.id).all()
    events: List[models.TaskEvent] = (
        db.query(models.TaskEvent).order_by(models.TaskEvent.created_at).all()
    )

    events_by_source: Dict[str, int] = defaultdict(int)
    for event in events:
        events_by_source[event.source] += 1

    grouped_events = _group_events_by_task(events)

    per_task = [
        _build_task_analytics(task, grouped_events.get(task.id, []))
        for task in tasks
    ]

    tasks_total = len(tasks)
    tasks_completed = sum(1 for task in tasks if task.progress >= 100)
    tasks_in_progress = sum(1 for task in tasks if 0 < task.progress < 100)
    tasks_not_started = tasks_total - tasks_completed - tasks_in_progress
    overall_progress = progress_tracker.calculate_overall_progress(tasks)

    completion_values = [
        entry.seconds_to_completion
        for entry in per_task
        if entry.seconds_to_completion is not None
    ]
    average_completion_seconds = None
    if completion_values:
        average_completion_seconds = sum(completion_values) / len(completion_values)

    last_event_at = events[-1].created_at if events else None

    return ProgressAnalyticsResult(
        tasks_total=tasks_total,
        tasks_completed=tasks_completed,
        tasks_in_progress=tasks_in_progress,
        tasks_not_started=tasks_not_started,
        overall_progress=overall_progress,
        events_total=len(events),
        events_by_source=dict(events_by_source),
        last_event_at=last_event_at,
        average_completion_seconds=average_completion_seconds,
        per_task=per_task,
    )

