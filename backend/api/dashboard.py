"""
Dashboard and analytics API routes
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..database import get_database_session
from ..models.database import User, UploadedFile, MappingTemplate, ProcessingTask
from ..models.schemas import DashboardResponse, DashboardStats, RecentFile
from ..api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", response_model=DashboardResponse)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get dashboard statistics and recent files"""
    
    # File statistics
    total_files = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id).count()
    
    files_processing = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id, UploadedFile.status == "processing")
        .count()
    )
    
    files_completed = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id, UploadedFile.status == "completed")
        .count()
    )
    
    files_error = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id, UploadedFile.status == "error")
        .count()
    )
    
    # Total records processed
    total_records = (
        db.query(func.sum(UploadedFile.records_processed))
        .filter(UploadedFile.user_id == current_user.id)
        .scalar() or 0
    )
    
    # Storage usage
    storage_used = (
        db.query(func.sum(UploadedFile.file_size))
        .filter(UploadedFile.user_id == current_user.id)
        .scalar() or 0
    )
    
    # Storage limits based on account type
    storage_limits = {
        "free": 1024 * 1024 * 1024,  # 1GB
        "premium": 10 * 1024 * 1024 * 1024  # 10GB
    }
    storage_limit = storage_limits.get(current_user.account_type, storage_limits["free"])
    
    # Recent files (last 5)
    recent_files = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(desc(UploadedFile.created_at))
        .limit(5)
        .all()
    )
    
    # Create response
    stats = DashboardStats(
        total_files=total_files,
        files_processing=files_processing,
        files_completed=files_completed,
        files_error=files_error,
        total_records_processed=total_records,
        account_type=current_user.account_type,
        storage_used=storage_used,
        storage_limit=storage_limit
    )
    
    recent_files_data = [
        RecentFile(
            id=file.id,
            filename=file.original_filename,
            status=file.status,
            created_at=file.created_at
        )
        for file in recent_files
    ]
    
    return DashboardResponse(
        stats=stats,
        recent_files=recent_files_data
    )

@router.get("/analytics/files")
async def get_file_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get file upload and processing analytics"""
    
    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    # Files uploaded per day
    uploads_per_day = (
        db.query(
            func.date(UploadedFile.created_at).label("date"),
            func.count(UploadedFile.id).label("count")
        )
        .filter(
            UploadedFile.user_id == current_user.id,
            func.date(UploadedFile.created_at) >= start_date
        )
        .group_by(func.date(UploadedFile.created_at))
        .order_by(func.date(UploadedFile.created_at))
        .all()
    )
    
    # Processing success rate
    total_processed = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.status.in_(["completed", "error"]),
            func.date(UploadedFile.created_at) >= start_date
        )
        .count()
    )
    
    successful_processed = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.status == "completed",
            func.date(UploadedFile.created_at) >= start_date
        )
        .count()
    )
    
    success_rate = (successful_processed / total_processed * 100) if total_processed > 0 else 0
    
    # File types distribution
    file_types = (
        db.query(
            UploadedFile.file_type,
            func.count(UploadedFile.id).label("count")
        )
        .filter(
            UploadedFile.user_id == current_user.id,
            func.date(UploadedFile.created_at) >= start_date
        )
        .group_by(UploadedFile.file_type)
        .all()
    )
    
    # Records processed over time
    records_per_day = (
        db.query(
            func.date(UploadedFile.processing_completed_at).label("date"),
            func.sum(UploadedFile.records_processed).label("records")
        )
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.processing_completed_at.isnot(None),
            func.date(UploadedFile.processing_completed_at) >= start_date
        )
        .group_by(func.date(UploadedFile.processing_completed_at))
        .order_by(func.date(UploadedFile.processing_completed_at))
        .all()
    )
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "uploads_per_day": [
            {"date": item.date.isoformat(), "count": item.count}
            for item in uploads_per_day
        ],
        "success_rate": round(success_rate, 2),
        "file_types": [
            {"type": item.file_type, "count": item.count}
            for item in file_types
        ],
        "records_per_day": [
            {"date": item.date.isoformat(), "records": item.records or 0}
            for item in records_per_day
        ]
    }

@router.get("/analytics/templates")
async def get_template_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get mapping template usage analytics"""
    
    # Most used templates
    popular_templates = (
        db.query(MappingTemplate)
        .filter(
            (MappingTemplate.user_id == current_user.id) |
            (MappingTemplate.is_public == True)
        )
        .order_by(desc(MappingTemplate.usage_count))
        .limit(10)
        .all()
    )
    
    # User's template statistics
    user_templates_count = (
        db.query(MappingTemplate)
        .filter(MappingTemplate.user_id == current_user.id)
        .count()
    )
    
    public_templates_count = (
        db.query(MappingTemplate)
        .filter(MappingTemplate.is_public == True)
        .count()
    )
    
    # Template usage over time (last 30 days)
    # This would require tracking template usage events in a separate table
    # For now, we'll return basic stats
    
    return {
        "popular_templates": [
            {
                "id": template.id,
                "name": template.name,
                "usage_count": template.usage_count,
                "is_public": template.is_public,
                "is_own": template.user_id == current_user.id
            }
            for template in popular_templates
        ],
        "stats": {
            "user_templates": user_templates_count,
            "available_public_templates": public_templates_count,
            "total_available": user_templates_count + public_templates_count
        }
    }

@router.get("/analytics/performance")
async def get_performance_analytics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """Get processing performance analytics"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Average processing time
    avg_processing_time = (
        db.query(
            func.avg(
                func.extract("epoch", UploadedFile.processing_completed_at) -
                func.extract("epoch", UploadedFile.processing_started_at)
            ).label("avg_seconds")
        )
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.processing_started_at.isnot(None),
            UploadedFile.processing_completed_at.isnot(None),
            UploadedFile.processing_started_at >= start_date
        )
        .scalar() or 0
    )
    
    # Processing errors analysis
    error_files = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.status == "error",
            UploadedFile.created_at >= start_date
        )
        .all()
    )
    
    # Error categories (simplified)
    error_categories = {}
    for file in error_files:
        if file.error_message:
            # Categorize errors (this is simplified)
            if "format" in file.error_message.lower():
                error_categories["format_error"] = error_categories.get("format_error", 0) + 1
            elif "permission" in file.error_message.lower():
                error_categories["permission_error"] = error_categories.get("permission_error", 0) + 1
            elif "size" in file.error_message.lower():
                error_categories["size_error"] = error_categories.get("size_error", 0) + 1
            else:
                error_categories["other_error"] = error_categories.get("other_error", 0) + 1
    
    # File size vs processing time correlation
    size_time_data = (
        db.query(
            UploadedFile.file_size,
            (func.extract("epoch", UploadedFile.processing_completed_at) -
             func.extract("epoch", UploadedFile.processing_started_at)).label("processing_seconds")
        )
        .filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.processing_started_at.isnot(None),
            UploadedFile.processing_completed_at.isnot(None),
            UploadedFile.processing_started_at >= start_date
        )
        .all()
    )
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "avg_processing_time_seconds": round(avg_processing_time, 2),
        "error_categories": error_categories,
        "size_vs_time": [
            {
                "file_size_mb": round(item.file_size / 1024 / 1024, 2),
                "processing_seconds": round(item.processing_seconds, 2)
            }
            for item in size_time_data
        ]
    }
