from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from .. import models, schemas
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


def calculate_overall_progress(tasks: list[models.Task]) -> float:
    if not tasks:
        return 0.0
    total = sum(task.progress for task in tasks)
    return round(total / (len(tasks) * 1.0), 2)


@router.get("/", response_model=schemas.ProgressReport)
def get_progress(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.ProgressReport:
    tasks = db.query(models.Task).order_by(models.Task.id).all()
    return schemas.ProgressReport(tasks=tasks, overall_progress=calculate_overall_progress(tasks))


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

    task.name = task_update.name
    task.progress = task_update.progress
    task.description = task_update.description
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/reset", response_model=schemas.ProgressReport, status_code=status.HTTP_202_ACCEPTED)
def reset_progress(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> schemas.ProgressReport:
    # Rehydrate tasks from configuration file to guarantee baseline values.
    config_tasks = settings.progress
    db.query(models.Task).delete()
    for entry in config_tasks:
        task = models.Task(
            name=entry["name"],
            progress=entry.get("progress", 0),
            description=entry.get("description"),
        )
        db.add(task)
    db.commit()
    tasks = db.query(models.Task).order_by(models.Task.id).all()
    return schemas.ProgressReport(tasks=tasks, overall_progress=calculate_overall_progress(tasks))
