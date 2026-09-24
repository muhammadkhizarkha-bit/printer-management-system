import os
import uuid
from fastapi import UploadFile
from ..config import UPLOADS_DIR

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def save_upload(file: UploadFile) -> str:
    if not file or not file.filename:
        return ""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return ""
    name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOADS_DIR, name)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return f"/static/uploads/{name}"
