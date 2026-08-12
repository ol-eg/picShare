import uuid
from pathlib import Path

from PIL import Image

from app.database import settings


def save_upload(file_bytes: bytes, original_name: str) -> str:
    ext = Path(original_name).suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    upload_path = Path(settings.upload_dir) / filename
    upload_path.write_bytes(file_bytes)

    thumb_path = Path(settings.thumb_dir) / filename
    with Image.open(upload_path) as img:
        img.thumbnail(settings.thumbnail_size)
        img.save(thumb_path)

    return filename
