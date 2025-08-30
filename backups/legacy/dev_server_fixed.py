#!/usr/bin/env python3
"""
Complete backend for ML Extractor FastAPI
"""

import uvicorn
import os
import tempfile
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

app = FastAPI(
    title="ML Extractor API",
    version="2.0.0-dev",
    description="ML Extractor Backend - Complete File Processing System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models
class ProcessingResponse(BaseModel):
    success: bool
    message: str
    output_file: Optional[str] = None
    processing_time: Optional[float] = None
    records_processed: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    mode: str
    message: str
    timestamp: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    token: Optional[str] = None

# Demo users database
DEMO_USERS = {
    "premium@test.com": {
        "id": 1,
        "email": "premium@test.com",
        "password": "Premium123!",
        "name": "Premium User",
        "first_name": "Premium",
        "last_name": "User",
        "account_type": "premium",
        "is_verified": True
    },
    "free@test.com": {
        "id": 2,
        "email": "free@test.com", 
        "password": "Free123!",
        "name": "Free User",
        "first_name": "Free",
        "last_name": "User",
        "account_type": "free",
        "is_verified": True
    }
}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ML Extractor API - Complete Development Mode",
        "version": "2.0.0-dev",
        "status": "development",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "file_upload": "/api/files/upload",
            "file_process": "/api/files/process",
            "ml_template_analysis": "/api/files/analyze-ml-template",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        mode="development",
        message="Backend is running in development mode",
        timestamp=datetime.now().isoformat()
    )

# API Status endpoint
@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "2.0.0-dev",
        "backend": "FastAPI",
        "frontend": "React + Tailwind",
        "features": {
            "authentication": "in_development",
            "file_processing": "available",
            "ml_template_analysis": "available",
            "ai_enhancement": "planned",
            "mapping_config": "in_development"
        },
        "supported_formats": ["xlsx", "xls", "csv", "pdf", "docx", "txt"]
    }

# File upload endpoint
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for processing"""
    try:
        # Validate file type
        allowed_extensions = {'.xlsx', '.xls', '.csv', '.pdf', '.docx', '.txt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "filename": safe_filename,
            "original_name": file.filename,
            "size": len(content),
            "type": file_extension,
            "upload_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# File processing endpoint
@app.post("/api/files/process", response_model=ProcessingResponse)
async def process_file(
    filename: str = Form(...),
    output_format: str = Form(default="xlsx"),
    ai_enhance: bool = Form(default=False)
):
    """Process uploaded file"""
    try:
        start_time = datetime.now()
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Simple processing simulation
        # In real implementation, this would call the actual processing logic
        output_filename = f"processed_{filename}"
        output_path = os.path.join(UPLOAD_DIR, output_filename)
        
        # For demo, just copy the file (real processing would happen here)
        import shutil
        shutil.copy2(file_path, output_path)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessingResponse(
            success=True,
            message=f"File processed successfully{'with AI enhancement' if ai_enhance else ''}",
            output_file=output_filename,
            processing_time=processing_time,
            records_processed=100  # Simulated
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# File download endpoint
@app.get("/api/files/download/{filename}")
async def download_file(filename: str):
    """Download processed file"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

# List files endpoint
@app.get("/api/files/")
async def list_files():
    """List uploaded files"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_processed": filename.startswith("processed_")
                })
        
        return {
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

# ML Template Analysis endpoint
@app.post("/api/files/analyze-ml-template")
async def analyze_ml_template_endpoint(file: UploadFile = File(...)):
    """Analyze uploaded file for ML template structure"""
    try:
        # Simple ML template analysis for now
        import pandas as pd
        
        # Validate file type
        allowed_extensions = {'.xlsx', '.xls', '.csv'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no soportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Save temporary file for analysis
        temp_filename = f"temp_ml_analysis_{file.filename}"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        # Save file temporarily
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Basic analysis
            if file_extension == '.csv':
                df = pd.read_csv(temp_path)
            else:
                df = pd.read_excel(temp_path)
            
            # Detect if it looks like an ML template
            columns = df.columns.tolist()
            ml_indicators = ['titulo', 'precio', 'stock', 'categoria', 'title', 'price', 'sku', 'descripcion', 'marca']
            is_ml_template = any(any(indicator.lower() in col.lower() for indicator in ml_indicators) for col in columns)
            
            total_products = len(df.dropna(how='all'))
            sample_data = df.head(3).to_dict('records') if not df.empty else []
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Mock mapping patterns for now
            mapping_patterns = None
            if is_ml_template:
                mapped_fields = [col for col in columns if any(ind.lower() in col.lower() for ind in ml_indicators)]
                confidence_score = min(0.95, (len(mapped_fields) / len(columns)) * 1.2)
                
                mapping_patterns = {
                    "summary": {
                        "confidence_score": confidence_score,
                        "mapped_fields": len(mapped_fields),
                        "total_fields": len(columns),
                        "mapping_success_rate": confidence_score * 100,
                        "high_confidence_mappings": len(mapped_fields),
                        "manual_review_needed": len(columns) - len(mapped_fields)
                    },
                    "mapping_pattern": {
                        "field_mappings": [
                            {
                                "source_column": col,
                                "target_field": (
                                    "titulo" if any(ind in col.lower() for ind in ['titulo', 'title', 'nombre']) else 
                                    "precio" if any(ind in col.lower() for ind in ['precio', 'price']) else
                                    "stock" if any(ind in col.lower() for ind in ['stock', 'cantidad', 'qty']) else
                                    "categoria" if any(ind in col.lower() for ind in ['categoria', 'category']) else
                                    "sku" if 'sku' in col.lower() or 'codigo' in col.lower() else
                                    "descripcion" if any(ind in col.lower() for ind in ['descripcion', 'description']) else
                                    "marca" if any(ind in col.lower() for ind in ['marca', 'brand']) else
                                    col.lower()
                                ),
                                "confidence": "high" if any(ind.lower() in col.lower() for ind in ml_indicators) else "medium",
                                "transformation_rule": None,
                                "examples": [str(df[col].iloc[i]) for i in range(min(2, len(df))) if pd.notna(df[col].iloc[i])]
                            }
                            for col in columns
                        ]
                    },
                    "next_steps": [
                        "✅ Revisar mapeos sugeridos",
                        "🔧 Validar transformaciones propuestas",
                        "⚙️ Configurar validaciones personalizadas",
                        "🚀 Procesar datos con el mapeo generado"
                    ]
                }
            
            return {
                "analysis": {
                    "is_ml_template": is_ml_template,
                    "template_structure": {
                        "obligatory_columns": {col: "texto" for col in columns if any(ind.lower() in col.lower() for ind in ml_indicators[:4])},
                        "data_start_row": 2,
                        "obligatory_row": 1,
                        "data_type_row": 1
                    } if is_ml_template else None,
                    "detected_columns": {col: "texto" for col in columns},
                    "validation_errors": [],
                    "recommendations": [
                        "✅ Archivo analizado correctamente",
                        f"📊 Se detectaron {len(columns)} columnas",
                        f"🎯 {len([col for col in columns if any(ind.lower() in col.lower() for ind in ml_indicators)])} columnas coinciden con campos ML estándar"
                    ] if is_ml_template else [
                        "⚠️ No parece ser una plantilla ML estándar",
                        "💡 Considera agregar columnas como: título, precio, stock, categoría"
                    ],
                    "total_products": total_products,
                    "sample_data": sample_data,
                },
                "mapping_patterns": mapping_patterns,
                "file_saved": is_ml_template,
                "status": "success" if is_ml_template else "warning",
                "message": "✅ Plantilla ML detectada y analizada" if is_ml_template else "⚠️ No se detectó estructura de plantilla ML estándar"
            }
            
        except Exception as analysis_error:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            raise HTTPException(
                status_code=500,
                detail=f"Error analizando archivo: {str(analysis_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando solicitud: {str(e)}"
        )

# Authentication endpoints
@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Demo login endpoint"""
    try:
        # Check if user exists
        if request.email not in DEMO_USERS:
            return AuthResponse(
                success=False,
                message="Email no encontrado"
            )
        
        user = DEMO_USERS[request.email]
        
        # Check password
        if request.password != user["password"]:
            return AuthResponse(
                success=False,
                message="Contraseña incorrecta"
            )
        
        # Generate demo token
        demo_token = f"demo_token_{user['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Return user data without password
        user_data = {k: v for k, v in user.items() if k != "password"}
        
        return AuthResponse(
            success=True,
            message=f"Bienvenido {user['name']}!",
            user=user_data,
            token=demo_token
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Error de login: {str(e)}"
        )

@app.get("/auth/me")
async def get_current_user():
    """Get current user info (demo endpoint)"""
    return {
        "user": {
            "id": 1,
            "email": "demo@test.com",
            "name": "Demo User",
            "account_type": "premium"
        },
        "authenticated": True
    }

@app.post("/auth/logout")
async def logout():
    """Demo logout endpoint"""
    return {"success": True, "message": "Sesión cerrada exitosamente"}

# Frontend-compatible API endpoints (matching React frontend expectations)
@app.post("/api/login", response_model=AuthResponse)
async def api_login(request: LoginRequest):
    """Frontend-compatible login endpoint"""
    return await login(request)

@app.get("/api/user")
async def api_get_current_user():
    """Frontend-compatible current user endpoint"""
    return await get_current_user()

@app.post("/api/logout")
async def api_logout():
    """Frontend-compatible logout endpoint"""
    return await logout()

if __name__ == "__main__":
    print("🚀 Starting ML Extractor Backend - FastAPI")
    print("📚 Documentation available at: http://localhost:8006/docs")
    print("🔍 Health check at: http://localhost:8006/health")
    print("")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8006,
        reload=False,
        log_level="info"
    )
