"""
Mapping configuration API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For static typing only
    from ..models.database import User

# Defer heavy imports (database, models) into function scope to avoid
# import-time SQLAlchemy/ORM side-effects when modules are loaded by the
# dev server via importlib.
from ..models.schemas import (
    MappingTemplateCreate, MappingTemplateUpdate, MappingTemplateResponse,
    PaginatedResponse, PaginationParams, BaseResponse
)

# Guard auth import similar to admin_settings
try:
    from backend.api.auth import get_current_user
except Exception:
    try:
        from ..api.auth import get_current_user
    except Exception:
        # In non-development contexts let import fail; dev fallback is handled
        # by the dev server when ENVIRONMENT=development via admin_settings.
        raise

router = APIRouter(prefix="/mapping", tags=["mapping"])

@router.post("/templates", response_model=MappingTemplateResponse)
async def create_mapping_template(
    template_data: MappingTemplateCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Create a new mapping template"""
    
    # Check if template name already exists for user
    # Import models at runtime
    from ..models.database import MappingTemplate

    existing = (
        db.query(MappingTemplate)
        .filter(
            MappingTemplate.user_id == current_user.id,
            MappingTemplate.name == template_data.name
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists"
        )
    
    # Create template
    template = MappingTemplate(
        user_id=current_user.id,
        name=template_data.name,
        description=template_data.description,
        mapping_config=template_data.mapping_config.dict(),
        is_public=template_data.is_public
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return MappingTemplateResponse.from_orm(template)

@router.get("/templates", response_model=PaginatedResponse)
async def list_mapping_templates(
    pagination: PaginationParams = Depends(),
    include_public: bool = True,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """List mapping templates (user's own + public templates)"""
    
    # Import models at runtime
    from ..models.database import MappingTemplate

    query = db.query(MappingTemplate)
    
    if include_public:
        # Include user's templates and public templates
        query = query.filter(
            (MappingTemplate.user_id == current_user.id) |
            (MappingTemplate.is_public == True)
        )
    else:
        # Only user's templates
        query = query.filter(MappingTemplate.user_id == current_user.id)
    
    # Get total count
    total = query.count()
    
    # Get templates with pagination
    templates = (
        query.order_by(MappingTemplate.usage_count.desc(), MappingTemplate.created_at.desc())
        .offset((pagination.page - 1) * pagination.size)
        .limit(pagination.size)
        .all()
    )
    
    # Calculate pages
    pages = (total + pagination.size - 1) // pagination.size
    
    return PaginatedResponse(
        items=[MappingTemplateResponse.from_orm(template) for template in templates],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )

@router.get("/templates/{template_id}", response_model=MappingTemplateResponse)
async def get_mapping_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Get a specific mapping template"""
    
    from ..models.database import MappingTemplate

    template = (
        db.query(MappingTemplate)
        .filter(
            MappingTemplate.id == template_id,
            (MappingTemplate.user_id == current_user.id) |
            (MappingTemplate.is_public == True)
        )
        .first()
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Increment usage count if not owner
    if template.user_id != current_user.id:
        template.usage_count += 1
        db.commit()
    
    return MappingTemplateResponse.from_orm(template)

@router.put("/templates/{template_id}", response_model=MappingTemplateResponse)
async def update_mapping_template(
    template_id: int,
    template_data: MappingTemplateUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Update a mapping template (only owner can update)"""
    
    from ..models.database import MappingTemplate

    template = (
        db.query(MappingTemplate)
        .filter(
            MappingTemplate.id == template_id,
            MappingTemplate.user_id == current_user.id
        )
        .first()
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission to update it"
        )
    
    # Check if new name conflicts (if name is being changed)
    if template_data.name and template_data.name != template.name:
        existing = (
            db.query(MappingTemplate)
            .filter(
                MappingTemplate.user_id == current_user.id,
                MappingTemplate.name == template_data.name,
                MappingTemplate.id != template_id
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this name already exists"
            )
    
    # Update fields
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "mapping_config" and value:
            setattr(template, field, value.dict())
        else:
            setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return MappingTemplateResponse.from_orm(template)

@router.delete("/templates/{template_id}")
async def delete_mapping_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Delete a mapping template (only owner can delete)"""
    
    from ..models.database import MappingTemplate

    template = (
        db.query(MappingTemplate)
        .filter(
            MappingTemplate.id == template_id,
            MappingTemplate.user_id == current_user.id
        )
        .first()
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you don't have permission to delete it"
        )
    
    db.delete(template)
    db.commit()
    
    return BaseResponse(
        success=True,
        message="Template deleted successfully"
    )

@router.post("/templates/{template_id}/set-default")
async def set_default_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(lambda: __import__('backend.database', fromlist=['get_database_session']).get_database_session())
):
    """Set a template as default for the user"""
    
    from ..models.database import MappingTemplate

    template = (
        db.query(MappingTemplate)
        .filter(
            MappingTemplate.id == template_id,
            (MappingTemplate.user_id == current_user.id) |
            (MappingTemplate.is_public == True)
        )
        .first()
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Remove default from other user's templates
    db.query(MappingTemplate).filter(
        MappingTemplate.user_id == current_user.id,
        MappingTemplate.is_default == True
    ).update({"is_default": False})
    
    # Set this template as default (only for user's own templates)
    if template.user_id == current_user.id:
        template.is_default = True
    
    db.commit()
    
    return BaseResponse(
        success=True,
        message="Default template updated successfully"
    )

@router.get("/fields/suggestions")
async def get_field_suggestions(
    file_type: str = "xlsx",
    current_user = Depends(get_current_user)
):
    """Get field mapping suggestions based on file type"""
    
    # Common field mappings based on file type
    suggestions = {
        "xlsx": {
            "common_source_fields": [
                "Product Name", "Nombre del Producto", "Title", "Titulo",
                "Description", "Descripcion", "Price", "Precio",
                "Category", "Categoria", "Brand", "Marca",
                "Stock", "Inventory", "SKU", "Code", "Codigo"
            ],
            "target_fields": [
                "title", "description", "price", "category_id",
                "brand", "stock_quantity", "sku", "weight",
                "dimensions", "color", "size", "material"
            ]
        },
        "csv": {
            "common_source_fields": [
                "name", "title", "description", "price", "category",
                "brand", "stock", "sku", "code", "weight", "color"
            ],
            "target_fields": [
                "title", "description", "price", "category_id",
                "brand", "stock_quantity", "sku", "weight",
                "dimensions", "color", "size", "material"
            ]
        }
    }
    
    return suggestions.get(file_type, suggestions["xlsx"])

@router.post("/validate")
async def validate_mapping_config(
    mapping_config: dict,
    current_user = Depends(get_current_user)
):
    """Validate a mapping configuration"""
    
    errors = []
    warnings = []
    
    # Basic validation
    if not mapping_config.get("fields"):
        errors.append("No field mappings defined")
    
    fields = mapping_config.get("fields", [])
    
    # Check for duplicate target fields
    target_fields = [field.get("target_field") for field in fields if field.get("target_field")]
    duplicates = set([field for field in target_fields if target_fields.count(field) > 1])
    
    if duplicates:
        errors.append(f"Duplicate target fields: {', '.join(duplicates)}")
    
    # Check for required fields without default values
    required_fields = [field for field in fields if field.get("required") and not field.get("default_value")]
    if required_fields:
        warnings.append(f"Required fields without default values: {', '.join([f['target_field'] for f in required_fields])}")
    
    # Check for empty source fields
    empty_source = [field for field in fields if not field.get("source_field")]
    if empty_source:
        warnings.append(f"Fields without source mapping: {', '.join([f['target_field'] for f in empty_source])}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
