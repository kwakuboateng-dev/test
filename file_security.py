"""
Enhanced file upload security with magic byte validation.
"""
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from config import settings
import hashlib
import uuid

# Allowed MIME types with their magic bytes
ALLOWED_MIME_TYPES = {
    'image/jpeg': [b'\xff\xd8\xff'],
    'image/png': [b'\x89PNG\r\n\x1a\n'],
    'image/gif': [b'GIF87a', b'GIF89a'],
    'image/webp': [b'RIFF'],
}

def validate_file_extension(filename: str) -> bool:
    """Validate file has allowed extension"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in settings.get_allowed_extensions_list()

def validate_file_size(file: UploadFile) -> bool:
    """Validate file size"""
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    return size <= settings.MAX_UPLOAD_SIZE

def validate_magic_bytes(file_content: bytes) -> bool:
    """Validate file content matches allowed types using magic bytes"""
    for mime_type, magic_bytes_list in ALLOWED_MIME_TYPES.items():
        for magic_bytes in magic_bytes_list:
            if file_content.startswith(magic_bytes):
                return True
    return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in '._-')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    name = name[:50]
    
    # Add unique prefix to prevent collisions
    unique_id = uuid.uuid4().hex[:8]
    
    return f"{unique_id}_{name}{ext}"

async def validate_and_save_upload(
    file: UploadFile,
    upload_dir: str = "uploads"
) -> str:
    """
    Comprehensive file validation and secure saving.
    
    Returns:
        str: Saved filename
    
    Raises:
        HTTPException: If validation fails
    """
    # Validate extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.get_allowed_extensions_list())}"
        )
    
    # Validate size
    if not validate_file_size(file):
        max_mb = settings.MAX_UPLOAD_SIZE / 1048576
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_mb}MB"
        )
    
    # Read file content
    content = await file.read()
    await file.seek(0)
    
    # Validate magic bytes
    if not validate_magic_bytes(content):
        raise HTTPException(
            status_code=400,
            detail="Invalid file content. File may be corrupted or not a valid image."
        )
    
    # Create upload directory
    upload_path = Path(upload_dir)
    upload_path.mkdir(exist_ok=True)
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    file_path = upload_path / safe_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return safe_filename

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file for integrity checking"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
