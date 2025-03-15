import aiofiles
import os
import asyncio
from pathlib import Path
from fastapi import UploadFile, HTTPException
from src.config.messages import ERROR_UPLOAD_FILE
from src.config.constants import STATIC_DIR, ADD_IMAGE_DIR


async def delete_file(file_name: str):
    file_path = Path(f"{STATIC_DIR}{file_name}")

    if file_path.exists():
        await asyncio.to_thread(os.remove, file_path)
    return 0


async def update_file(file: UploadFile, meal):
    ext = Path(file.filename).suffix
    new_filename = f"{ADD_IMAGE_DIR}{meal.id}{ext}"
    new_filepath = f"{STATIC_DIR}{new_filename}"

    try:
        await delete_file(new_filename)

        file_path = Path(new_filepath)

        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(1024):
                await f.write(chunk)

        return new_filename

    except Exception as e:
        raise HTTPException(status_code=500, detail=ERROR_UPLOAD_FILE.format(error=str(e)))
