from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..services import progress_tracker

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/", response_model=schemas.ProgressReport)
def get_progress(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.ProgressReport:
    progress_settings = getattr(settings, "progress_settings", None)
    history_limit = 20
    if progress_settings is not None:
        history_limit = int(progress_settings.get("event_history_limit", default=20))

    tasks = db.query(models.Task).order_by(models.Task.id).all()
    events = progress_tracker.get_recent_events(db, limit=history_limit)
    overall = progress_tracker.calculate_overall_progress(tasks)
    return schemas.ProgressReport(tasks=tasks, events=events, overall_progress=overall)


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskBase,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TaskResponse:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    previous_progress = task.progress
    task.name = task_update.name
    task.progress = task_update.progress
    task.description = task_update.description
    db.add(task)

    if task_update.progress != previous_progress:
        progress_tracker.apply_progress_event(
            db,
            task=task,
            progress_value=task_update.progress,
            source="manual-update",
            note="Progress updated via dashboard",
        )

    db.commit()
    db.refresh(task)
    return task


@router.post("/reset", response_model=schemas.ProgressReport, status_code=status.HTTP_202_ACCEPTED)
def reset_progress(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.ProgressReport:
    # Rehydrate tasks from configuration file to guarantee baseline values.
    progress_tracker.reset_progress_from_config(db)
    db.commit()
    tasks = db.query(models.Task).order_by(models.Task.id).all()
    overall = progress_tracker.calculate_overall_progress(tasks)
    return schemas.ProgressReport(tasks=tasks, events=[], overall_progress=overall)


@router.post("/events", response_model=schemas.TaskEventResponse, status_code=status.HTTP_201_CREATED)
def create_progress_event(
    event: schemas.TaskEventCreate,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TaskEventResponse:
    default_source = "api"
    progress_settings = getattr(settings, "progress_settings", None)
    if progress_settings is not None:
        default_source = progress_settings.get("default_event_source", default="api")

    task = progress_tracker.get_or_create_task(db, event.task_name)
    recorded = progress_tracker.apply_progress_event(
        db,
        task=task,
        progress_value=event.progress,
        source=event.source or default_source,
        note=event.note,
    )
    db.commit()
    db.refresh(recorded)
    return recorded


@router.get("/events", response_model=List[schemas.TaskEventResponse])
def list_progress_events(
    limit: int = Query(None, ge=1, le=200),
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.TaskEventResponse]:
    progress_settings = getattr(settings, "progress_settings", None)
    history_limit = 20
    if progress_settings is not None:
        history_limit = int(progress_settings.get("event_history_limit", default=20))
    if limit is not None:
        history_limit = min(history_limit, limit)
    events = progress_tracker.get_recent_events(db, limit=history_limit)
    return events
