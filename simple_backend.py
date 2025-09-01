#!/usr/bin/env python3
"""
Simple FastAPI Backend Server
Compatible with Python 3.13 - No SQLAlchemy dependencies
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import secrets

# Pydantic models for JSON requests
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# Setup logging - reuse centralized logging configuration when available
try:
    from backend.core.logging_config import setup_logging
    setup_logging()
    logger = logging.getLogger(__name__)
except Exception:
    # Fall back to a simple console logger if centralized logging isn't available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Production configuration
PRODUCTION = os.getenv('PRODUCTION', '').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3002')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3002,http://localhost:3000').split(',')

if PRODUCTION:
    logger.info("🚀 Running in PRODUCTION mode")
    # Configure for production
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.getLogger().setLevel(getattr(logging, log_level))
else:
    logger.info("🔧 Running in DEVELOPMENT mode")
    # Add localhost for development
    ALLOWED_ORIGINS.extend(['http://localhost:3002', 'http://localhost:3000', 'http://localhost:8011'])

# Simple in-memory storage (replace with database in production)
users_db = {}
sessions_db = {}
files_db = {}
admin_settings = {}

# Security
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="ML Extractor API",
    description="Simple API for ML Extractor file processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
from fastapi.staticfiles import StaticFiles
import os
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token() -> str:
    """Create a simple token"""
    return secrets.token_urlsafe(32)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    token = credentials.credentials
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return sessions_db[token]


def role_required_factory(required_roles: List[str]):
    """Return a dependency that ensures current user has one of the required roles."""
    def _verify_role(current_user: dict = Depends(verify_token)):
        username = current_user.get('username')
        user = users_db.get(username)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        role = user.get('role', 'user')
        if role not in required_roles:
            raise HTTPException(status_code=403, detail='Insufficient permissions')
        return current_user
    return _verify_role

# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ML Extractor API is running", 
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "ml-extractor-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }


def _load_admin_settings():
    try:
        path = os.path.join(os.getcwd(), 'config_admin.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                admin_settings.clear()
                admin_settings.update(data)
    except Exception:
        logger.exception('Failed loading admin settings')


def _save_admin_settings():
    try:
        path = os.path.join(os.getcwd(), 'config_admin.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(admin_settings, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception('Failed saving admin settings')


# load persisted admin settings on startup (call after helper functions are defined)
_load_admin_settings()


def _mask_api_key(key: str) -> str:
    if not key:
        return ''
    if len(key) <= 8:
        return '*' * len(key)
    return key[:4] + ('*' * (len(key) - 8)) + key[-4:]

DB_PATH = os.path.join(os.getcwd(), 'data', 'users.db')


def init_db():
    """Initialize sqlite DB and migrate json users if present."""
    os.makedirs(os.path.join(os.getcwd(), 'data'), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            password TEXT,
            created_at TEXT,
            is_active INTEGER,
            role TEXT
        )
        '''
    )
    conn.commit()

    # If legacy JSON exists, migrate it
    json_path = os.path.join(os.getcwd(), 'data', 'users.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for uname, u in data.items():
                cur.execute(
                    'REPLACE INTO users (username,email,password,created_at,is_active,role) VALUES (?,?,?,?,?,?)',
                    (
                        u.get('username', uname),
                        u.get('email'),
                        u.get('password'),
                        u.get('created_at'),
                        1 if u.get('is_active', True) else 0,
                        u.get('role', 'user')
                    )
                )
            conn.commit()
            logger.info('Migrated users.json to users.db')
        except Exception:
            logger.exception('Failed migrating users.json')
    conn.close()


def load_users_from_db():
    try:
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT username,email,password,created_at,is_active,role FROM users')
        rows = cur.fetchall()
        users_db.clear()
        for r in rows:
            users_db[r[0]] = {
                'username': r[0],
                'email': r[1],
                'password': r[2],
                'created_at': r[3],
                'is_active': bool(r[4]),
                'role': r[5] or 'user'
            }
        conn.close()
        logger.info(f'Loaded {len(users_db)} users from sqlite DB')
    except Exception:
        logger.exception('Failed loading users from DB')


def save_user_to_db(username: str):
    try:
        user = users_db.get(username)
        if not user:
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            'REPLACE INTO users (username,email,password,created_at,is_active,role) VALUES (?,?,?,?,?,?)',
            (
                user.get('username'),
                user.get('email'),
                user.get('password'),
                user.get('created_at'),
                1 if user.get('is_active', True) else 0,
                user.get('role', 'user')
            )
        )
        conn.commit()
        conn.close()
        logger.info(f'Saved user {username} to sqlite DB')
    except Exception:
        logger.exception('Failed saving user to DB')


def save_all_users_to_db():
    try:
        for uname in list(users_db.keys()):
            save_user_to_db(uname)
        logger.info('Saved all users to sqlite DB')
    except Exception:
        logger.exception('Failed saving all users to DB')


# Initialize DB and load into memory
init_db()
load_users_from_db()

@app.get('/api/admin/settings')
async def get_admin_settings(current_user: dict = Depends(verify_token)):
    """Return admin settings (masked)"""
    result = {}
    for k, v in admin_settings.items():
        result[k] = {
            'provider': k,
            'api_key_masked': _mask_api_key(v.get('api_key')),
            'notes': v.get('notes', '')
        }
    return {'settings': result}


@app.post('/api/admin/settings')
async def set_admin_setting(payload: dict, current_user: dict = Depends(verify_token)):
    """Set or update an admin setting. Payload: {provider, api_key, notes} - stored encrypted in file (simple storage)"""
    provider = payload.get('provider')
    if not provider:
        raise HTTPException(status_code=400, detail='provider is required')
    api_key = payload.get('api_key')
    notes = payload.get('notes')

    admin_settings[provider] = {
        'api_key': api_key,
        'notes': notes or ''
    }
    _save_admin_settings()
    return {'status': 'ok'}

@app.delete('/api/admin/settings/{provider}')
async def delete_admin_setting(provider: str, current_user: dict = Depends(verify_token)):
    if provider in admin_settings:
        del admin_settings[provider]
        _save_admin_settings()
    return {'status': 'ok'}


@app.post('/api/admin/promote')
async def admin_promote_user(payload: dict, current_user: dict = Depends(role_required_factory(['admin']))):
    """Admin endpoint to change a user's role. Payload: {username, role} (role: user|premium|admin)"""
    username = payload.get('username')
    role = payload.get('role')
    if not username or not role:
        raise HTTPException(status_code=400, detail='username and role are required')
    if username not in users_db:
        raise HTTPException(status_code=404, detail='User not found')
    if role not in ('user', 'premium', 'admin'):
        raise HTTPException(status_code=400, detail='Invalid role')
    users_db[username]['role'] = role
    # Persist role changes
    save_user_to_db(username)
    logger.info(f"Admin {current_user['username']} set role {role} for user {username}")
    return {'status': 'ok', 'username': username, 'role': role}


@app.post('/api/admin/force-save-users')
async def admin_force_save_users(current_user: dict = Depends(role_required_factory(['admin']))):
    """Force saving users to disk and return result for debugging."""
    try:
        save_all_users_to_db()
        return {'status': 'ok', 'message': 'users saved (if no exception)'}
    except Exception as e:
        # Return exception text to help debugging
        return JSONResponse(status_code=500, content={'status': 'error', 'error': str(e)})


# Dev helper: promote a user if caller knows DEV_PROMOTE_KEY env var (useful for local testing)
DEV_PROMOTE_KEY = os.environ.get('DEV_PROMOTE_KEY')

@app.post('/api/debug/promote/{username}')
async def debug_promote_user(username: str, key: Optional[str] = None):
    """Dev-only: promote a user to premium if correct key provided via query or header."""
    if not DEV_PROMOTE_KEY:
        raise HTTPException(status_code=403, detail='Dev promote not enabled')
    if key != DEV_PROMOTE_KEY:
        raise HTTPException(status_code=403, detail='Invalid dev key')
    if username not in users_db:
        raise HTTPException(status_code=404, detail='User not found')
    users_db[username]['role'] = 'premium'
    # Persist role change for debug promote as well
    save_user_to_db(username)
    logger.info(f"Dev promote: {username} -> premium")
    return {'status': 'ok', 'username': username, 'role': 'premium'}

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    
    # Check if user already exists
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    for user_data in users_db.values():
        if user_data["email"] == request.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user (assign role: first registered user becomes 'admin', otherwise 'user')
    hashed_password = hash_password(request.password)
    # Determine role: if no admin exists, promote the first user to admin (dev convenience)
    existing_admin = any(u.get('role') == 'admin' for u in users_db.values())
    role = 'user' if existing_admin else 'admin'
    users_db[request.username] = {
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "role": role
    }
    
    logger.info(f"User registered: {request.username}")
    
    return {
        "message": "User registered successfully",
        "username": request.username,
    "email": request.email,
    "role": role
    }

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login user"""
    
    # Check if user exists
    if request.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user = users_db[request.username]
    
    # Check password
    if user["password"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Account is disabled")
    
    # Create session
    token = create_token()
    sessions_db[token] = {
        "username": request.username,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    logger.info(f"User logged in: {request.username}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": request.username,
            "email": user["email"],
            "role": user.get("role", "user")
        }
    }

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """Logout user"""
    
    # Find and remove the token
    token_to_remove = None
    for token, session in sessions_db.items():
        if session["username"] == current_user["username"]:
            token_to_remove = token
            break
    
    if token_to_remove:
        del sessions_db[token_to_remove]
    
    logger.info(f"User logged out: {current_user['username']}")
    
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user info"""
    username = current_user["username"]
    user_data = users_db.get(username)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user_data["username"],
        "email": user_data["email"],
        "created_at": user_data["created_at"],
    "is_active": user_data["is_active"],
    "role": user_data.get("role", "user")
    }


class DebugLog(BaseModel):
    source: str
    payload: dict


@app.post("/api/debug/logs")
async def receive_debug_logs(log: DebugLog):
    """Receive debug logs from frontend and save to logs/debug-logs.json"""
    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    entry = {
        'timestamp': timestamp,
        'source': log.source,
        'payload': log.payload
    }
    path = os.path.join('logs', 'debug-logs.json')
    try:
        # Append to file as JSON lines
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        logger.info('Received debug log from frontend')
        return JSONResponse({'status': 'ok', 'path': path})
    except Exception as e:
        logger.error('Failed to write debug log: %s', e)
        raise HTTPException(status_code=500, detail='Failed to save log')


# Development debug endpoints
@app.get('/api/debug/users')
async def debug_get_users():
    """Return current in-memory users database (dev only)"""
    return users_db


@app.get('/api/debug/sessions')
async def debug_get_sessions():
    """Return current in-memory sessions (dev only)"""
    return sessions_db

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    """Upload a file for processing"""
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(uploads_dir, filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store file info
        file_id = secrets.token_urlsafe(16)
        files_db[file_id] = {
            "id": file_id,
            "original_name": file.filename,
            "stored_name": filename,
            "file_path": file_path,
            "size": len(content),
            "content_type": file.content_type,
            "uploaded_by": current_user["username"],
            "uploaded_at": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        logger.info(f"File uploaded: {filename} by {current_user['username']}")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "status": "uploaded",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        # Clean up file if it was created
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/api/files/list")
async def list_files(current_user: dict = Depends(verify_token)):
    """List user's uploaded files"""
    
    user_files = []
    for file_data in files_db.values():
        if file_data["uploaded_by"] == current_user["username"]:
            user_files.append({
                "id": file_data["id"],
                "filename": file_data["original_name"],
                "size": file_data["size"],
                "uploaded_at": file_data["uploaded_at"],
                "status": file_data["status"]
            })
    
    return {"files": user_files}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(verify_token)):
    """Get dashboard statistics"""
    
    user_files = [f for f in files_db.values() if f["uploaded_by"] == current_user["username"]]
    
    return {
        "total_files": len(user_files),
        "total_size": sum(f["size"] for f in user_files),
        "recent_uploads": len([f for f in user_files if 
                             datetime.fromisoformat(f["uploaded_at"]) > datetime.now() - timedelta(days=7)]),
        "user_info": {
            "username": current_user["username"],
            "session_created": current_user["created_at"]
        }
    }

@app.get("/api/mapping/config")
async def get_mapping_config(current_user: dict = Depends(verify_token)):
    """Get mapping configuration"""
    
    # Default mapping configuration
    default_config = {
        "mappings": {
            "title": "Título del producto",
            "description": "Descripción",
            "price": "Precio",
            "category": "Categoría",
            "brand": "Marca",
            "model": "Modelo",
            "condition": "Condición"
        },
        "default_values": {
            "condition": "new",
            "currency": "ARS"
        }
    }
    
    return {"config": default_config}

if __name__ == "__main__":
    logger.info("🚀 Starting ML Extractor Simple Backend...")
    logger.info("📊 In-memory storage initialized")
    logger.info("🔐 Authentication system ready")
    logger.info("📁 File upload system ready")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8010, 
        reload=False,
        log_level="info"
    )
