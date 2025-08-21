"""
File handling API routes
"""

import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_database_session
from ..models.database import User, UploadedFile, ProcessingTask
from ..models.schemas import (
    FileUploadResponse, FileResponse, FileProcessingRequest,
    TaskResponse, PaginatedResponse, PaginationParams
)
from ..api.auth import get_current_user
from ..core.config import settings
from ..services.file_processor import FileProcessorService
from ..services.ml_processor import MLProcessorService

router = APIRouter(prefix="/files", tags=["files"])

# Helper functions
def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return any(filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS)

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """Save uploaded file and return file path and filename"""
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create user directory
    user_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(user_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path, unique_filename

# Routes
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Upload a file"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Save file
    try:
        file_path, unique_filename = save_uploaded_file(file, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    db_file = UploadedFile(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=os.path.splitext(file.filename)[1],
        mime_type=file.content_type or "application/octet-stream"
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return FileUploadResponse.from_orm(db_file)

@router.get("/", response_model=PaginatedResponse)
async def list_files(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """List user's files with pagination"""
    
    # Get total count
    total = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id).count()
    
    # Get files with pagination
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.created_at.desc())
        .offset((pagination.page - 1) * pagination.size)
        .limit(pagination.size)
        .all()
    )
    
    # Calculate pages
    pages = (total + pagination.size - 1) // pagination.size
    
    return PaginatedResponse(
        items=[FileResponse.from_orm(file) for file in files],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get file details"""
    
    file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id, UploadedFile.user_id == current_user.id)
        .first()
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse.from_orm(file)

@router.post("/{file_id}/process", response_model=TaskResponse)
async def process_file(
    file_id: int,
    processing_request: FileProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Process a file with mapping and optional AI enhancement"""
    
    # Get file
    file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id, UploadedFile.user_id == current_user.id)
        .first()
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if file.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is already being processed"
        )
    
    # Create processing task
    task_id = str(uuid.uuid4())
    task = ProcessingTask(
        task_id=task_id,
        user_id=current_user.id,
        file_id=file.id,
        task_type="file_processing",
        status="pending"
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Update file status
    file.status = "processing"
    file.processing_started_at = datetime.utcnow()
    db.commit()
    
    # Start background processing
    background_tasks.add_task(
        process_file_background,
        task_id,
        file_id,
        processing_request.dict(),
        current_user.id
    )
    
    return TaskResponse.from_orm(task)

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Download original or processed file"""
    
    file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id, UploadedFile.user_id == current_user.id)
        .first()
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Use output file if available, otherwise original file
    file_path = file.output_file_path or file.file_path
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Determine filename for download
    if file.output_file_path:
        download_filename = f"processed_{file.original_filename}"
    else:
        download_filename = file.original_filename
    
    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type="application/octet-stream"
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Delete a file"""
    
    file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id, UploadedFile.user_id == current_user.id)
        .first()
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete files from disk
    try:
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        if file.output_file_path and os.path.exists(file.output_file_path):
            os.remove(file.output_file_path)
    except Exception as e:
        print(f"Error deleting file from disk: {e}")
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    return {"success": True, "message": "File deleted successfully"}

# Background task function
async def process_file_background(
    task_id: str,
    file_id: int,
    processing_config: dict,
    user_id: int
):
    """Background task to process file"""
    
    # This would be implemented with your actual file processing logic
    # For now, it's a placeholder
    
    from ..database import SessionLocal
    db = SessionLocal()
    
    try:
        # Get task and file
        task = db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()
        file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        
        if not task or not file:
            return
        
        # Update task status
        task.status = "running"
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Process file using your existing services
        processor = FileProcessorService()
        ml_processor = MLProcessorService()
        
        # Update progress
        task.progress = 25.0
        task.current_step = "Reading file"
        db.commit()
        
        # Simulate processing steps
        # In real implementation, this would use your existing ML processing logic
        
        task.progress = 50.0
        task.current_step = "Applying mapping"
        db.commit()
        
        if processing_config.get("ai_enhancement"):
            task.progress = 75.0
            task.current_step = "AI enhancement"
            db.commit()
        
        # Complete processing
        task.status = "completed"
        task.progress = 100.0
        task.current_step = "Completed"
        task.completed_at = datetime.utcnow()
        
        file.status = "completed"
        file.processing_completed_at = datetime.utcnow()
        file.records_processed = 100  # Replace with actual count
        file.records_successful = 95  # Replace with actual count
        file.records_errors = 5  # Replace with actual count
        
        db.commit()
        
    except Exception as e:
        # Handle error
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        
        file.status = "error"
        file.error_message = str(e)
        file.processing_completed_at = datetime.utcnow()
        
        db.commit()
        
    finally:
        db.close()
