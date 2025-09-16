from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import SessionLocal, engine
from .models import Base, Task
from .routers import auth as auth_router
from .routers import chat as chat_router
from .routers import progress as progress_router

app = FastAPI(title=settings.app.name, version=settings.app.version)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    # Ensure progress tasks exist based on config
    from sqlalchemy.orm import Session

    session: Session = SessionLocal()
    try:
        existing_tasks = {task.name: task for task in session.query(Task).all()}
        for entry in settings.progress:
            task = existing_tasks.get(entry["name"])
            if task:
                task.progress = entry.get("progress", task.progress)
                task.description = entry.get("description", task.description)
            else:
                session.add(
                    Task(
                        name=entry["name"],
                        progress=entry.get("progress", 0),
                        description=entry.get("description"),
                    )
                )
        session.commit()
    finally:
        session.close()


origins: List[str] = list(settings.cors.allowed_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(progress_router.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


config_path = Path(__file__).resolve().parent.parent / "config"
media_path = Path(settings.files.media_root)
media_path.mkdir(parents=True, exist_ok=True)

app.mount("/config", StaticFiles(directory=config_path), name="config")
app.mount("/media", StaticFiles(directory=media_path), name="media")

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
