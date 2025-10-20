import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path

from app.core.config.settings import settings


async def save_upload_file(
    upload_file: UploadFile, 
    folder: str = "",
    filename: Optional[str] = None
) -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the filename
    """
    try:
        # Ensure upload directory exists
        upload_dir = settings.UPLOAD_DIRECTORY
        if folder:
            upload_dir = os.path.join(upload_dir, folder)
        
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename if not provided
        if not filename:
            # Get file extension
            ext = Path(upload_file.filename).suffix
            filename = f"{uuid.uuid4()}{ext}"
        
        # Create file path
        file_path = os.path.join(upload_dir, filename)
        
        # Write file contents
        content = await upload_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return filename
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


def delete_file(filepath: str) -> bool:
    """
    Delete a file from the filesystem
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception:
        return False