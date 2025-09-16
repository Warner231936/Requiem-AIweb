from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from .. import models, schemas
from ..database import get_db
from ..services.responder import generate_ai_response


def advance_task_progress(db: Session) -> None:
    task = (
        db.query(models.Task)
        .filter(models.Task.progress < 100)
        .order_by(asc(models.Task.updated_at))
        .first()
    )
    if task:
        increment = 7 if task.progress <= 90 else max(1, 100 - task.progress)
        task.progress = min(100, task.progress + increment)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history", response_model=List[schemas.MessageResponse])
def chat_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.MessageResponse]:
    messages = (
        db.query(models.Message)
        .filter(models.Message.user_id == current_user.id)
        .order_by(desc(models.Message.created_at))
        .limit(limit)
        .all()
    )
    return list(reversed(messages))


@router.post("/message", response_model=List[schemas.MessageResponse], status_code=status.HTTP_201_CREATED)
def post_message(
    message: schemas.MessageCreate,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.MessageResponse]:
    user_message = models.Message(user_id=current_user.id, role="user", content=message.content.strip())
    ai_content = generate_ai_response(message.content)
    ai_message = models.Message(user_id=current_user.id, role="ai", content=ai_content)

    db.add_all([user_message, ai_message])
    db.flush()
    advance_task_progress(db)
    db.commit()
    db.refresh(user_message)
    db.refresh(ai_message)

    return [user_message, ai_message]
