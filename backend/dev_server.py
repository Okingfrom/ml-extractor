#!/usr/bin/env python3
"""
Complete backend for ML Extractor FastAPI
"""

if __name__ == "__main__":
    import uvicorn
    import os
    import tempfile
    from datetime import datetime
    from typing import List, Optional
    
    print("🚀 Starting ML Extractor Backend - FastAPI")
    print("📚 Documentation available at: http://localhost:8004/docs")
    print("🔍 Health check at: http://localhost:8004/health")
    print("")
    
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
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "*"],
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
    
    # Demo authentication endpoints
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
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )
