from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import auth as auth_utils
from .. import models, schemas
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(
    username: str = Form(..., min_length=3, max_length=50),
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    profile_picture: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
) -> schemas.UserResponse:
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = auth_utils.get_password_hash(password)
    user = models.User(username=username, email=email, hashed_password=hashed_password)

    media_root = Path(settings.files.media_root)
    profile_dir = Path(settings.files.profile_pictures)
    media_root.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    if profile_picture is not None:
        filename = f"{username}_profile{Path(profile_picture.filename).suffix}" if profile_picture.filename else f"{username}_profile.jpg"
        file_location = profile_dir / filename
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)
        user.profile_image = file_location.as_posix()

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> schemas.Token:
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    access_token = auth_utils.create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth_utils.get_current_user)) -> schemas.UserResponse:
    return current_user
