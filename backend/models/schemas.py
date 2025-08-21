"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class AccountType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class UserType(str, Enum):
    USER = "user"
    ADMIN = "admin"

class FileStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Base models
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# User models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    account_type: AccountType
    user_type: UserType
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

class VerificationRequest(BaseModel):
    token: str

# File models
class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: FileStatus
    created_at: datetime

    class Config:
        from_attributes = True

class FileProcessingRequest(BaseModel):
    mapping_template_id: Optional[int] = None
    ai_enhancement: bool = False
    custom_mapping: Optional[Dict[str, Any]] = None

class FileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    status: FileStatus
    records_processed: int
    records_successful: int
    records_errors: int
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Mapping models
class MappingField(BaseModel):
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = False

class MappingConfig(BaseModel):
    fields: List[MappingField]
    ai_enhancement: bool = False
    validation_rules: Optional[Dict[str, Any]] = None

class MappingTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    mapping_config: MappingConfig
    is_public: bool = False

class MappingTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mapping_config: Optional[MappingConfig] = None
    is_public: Optional[bool] = None

class MappingTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    mapping_config: MappingConfig
    is_public: bool
    is_default: bool
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Task models
class TaskResponse(BaseModel):
    id: int
    task_id: str
    task_type: str
    status: TaskStatus
    progress: float
    current_step: Optional[str]
    total_steps: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True

# Dashboard models
class DashboardStats(BaseModel):
    total_files: int
    files_processing: int
    files_completed: int
    files_error: int
    total_records_processed: int
    account_type: AccountType
    storage_used: int  # in bytes
    storage_limit: int  # in bytes

class RecentFile(BaseModel):
    id: int
    filename: str
    status: FileStatus
    created_at: datetime

class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_files: List[RecentFile]

# API Key models
class ApiKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    rate_limit: Optional[int] = 1000
    expires_at: Optional[datetime] = None

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    permissions: List[str]
    rate_limit: int
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyWithSecret(ApiKeyResponse):
    api_key: str  # Full key only shown once

# Error models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    details: List[Dict[str, Any]]

# Pagination models
class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Size must be between 1 and 100')
        return v

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
