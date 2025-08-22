"""
File handling API routes
"""

import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from ..models.database import User

# Guard auth import similar to admin_settings to allow dev-server imports
try:
    from backend.api.auth import get_current_user
except Exception:
    try:
        from ..api.auth import get_current_user
    except Exception:
        # Let it fail outside development; dev fallback handled elsewhere
        raise

# Defer heavy DB/model imports into function bodies to avoid import-time side-effects
from ..models.schemas import (
    FileUploadResponse, FileResponse as FileSchema, FileProcessingRequest,
    TaskResponse, PaginatedResponse, PaginationParams
)
from ..services.ml_template_processor import process_ml_template
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
    current_user: 'User' = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
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
    
    # Create database record (import models at runtime)
    from ..models.database import UploadedFile

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
    current_user: 'User' = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """List user's files with pagination"""
    
    # Get total count
    from ..models.database import UploadedFile

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
        items=[FileSchema.from_orm(file) for file in files],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: 'User' = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Get file details"""
    
    from ..models.database import UploadedFile

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
    
    return FileSchema.from_orm(file)

@router.post("/{file_id}/process", response_model=TaskResponse)
async def process_file(
    file_id: int,
    processing_request: FileProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: 'User' = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Process a file with mapping and optional AI enhancement"""
    
    # Get file
    from ..models.database import UploadedFile

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
    
    # Create processing task (import models at runtime)
    from ..models.database import ProcessingTask

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

@router.post("/analyze-ml-template")
async def analyze_ml_template(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
) -> Dict[str, Any]:
    """
    Analyze uploaded file to detect Mercado Libre template structure
    """
    
    # Validate file type
    allowed_extensions = {'.xlsx', '.xls', '.csv'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no soportado. Use: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (50MB for premium, 5MB for free users)
    max_size = 50 * 1024 * 1024 if current_user.subscription_type == "premium" else 5 * 1024 * 1024
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo muy grande. Tamaño máximo: {max_size / 1024 / 1024:.1f}MB"
        )
    
    # Save temporary file for analysis
    temp_filename = f"temp_ml_analysis_{uuid.uuid4()}{file_extension}"
    temp_path = os.path.join("uploads", temp_filename)
    
    try:
        # Save file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze ML template
        analysis_result = process_ml_template(temp_path)
        
        # If it's a valid ML template, save to database
        if analysis_result['analysis']['is_ml_template']:
            # Save file permanently
            permanent_filename = f"ml_template_{current_user.id}_{uuid.uuid4()}{file_extension}"
            permanent_path = os.path.join("uploads", permanent_filename)
            shutil.move(temp_path, permanent_path)
            
            # Create database record
            from ..models.database import UploadedFile

            db_file = UploadedFile(
                user_id=current_user.id,
                filename=file.filename,
                original_filename=file.filename,
                file_path=permanent_path,
                file_size=file_size,
                file_type=file.content_type,
                status="analyzed",
                metadata=json.dumps({
                    "ml_analysis": analysis_result['analysis'],
                    "template_type": "mercado_libre",
                    "analysis_date": datetime.now().isoformat()
                })
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            
            # Add file ID to response
            analysis_result['file_id'] = db_file.id
            analysis_result['file_saved'] = True
        else:
            # Remove temporary file if not ML template
            if os.path.exists(temp_path):
                os.remove(temp_path)
            analysis_result['file_saved'] = False
        
        return analysis_result
        
    except Exception as e:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analizando archivo: {str(e)}"
        )

@router.get("/{file_id}/ml-analysis")
async def get_ml_analysis(
    file_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
) -> Dict[str, Any]:
    """
    Get ML template analysis for a previously uploaded file
    """
    
    from ..models.database import UploadedFile

    file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id, UploadedFile.user_id == current_user.id)
        .first()
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    # Check if file has ML analysis metadata
    if not file.metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene análisis ML disponible"
        )
    
    try:
        metadata = json.loads(file.metadata)
        ml_analysis = metadata.get('ml_analysis')
        
        if not ml_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontró análisis ML en el archivo"
            )
        
        return {
            'file_id': file.id,
            'filename': file.original_filename,
            'analysis': ml_analysis,
            'status': 'success'
        }
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error leyendo metadatos del archivo"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Download original or processed file"""
    
    from ..models.database import UploadedFile

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
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Delete a file"""
    
    from ..models.database import UploadedFile

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
    from ..models.database import ProcessingTask, UploadedFile

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
