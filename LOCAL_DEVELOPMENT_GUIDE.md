# 🚀 Local Development Guide for ML-Extractor

## Quick Start - Test UI Locally

### 📋 Prerequisites
- Node.js (v16+) installed
- Python 3.8+ installed
- Git repository cloned

### 🔧 Method 1: Full React + FastAPI Setup (Recommended)

#### Step 1: Start the Backend (FastAPI)
```powershell
# In PowerShell - Terminal 1
cd c:\Users\equipo\Desktop\ml-extractor

# Setup Python environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend on port 8009
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8009
```

#### Step 2: Start the Frontend (React)
```powershell
# In PowerShell - Terminal 2
cd c:\Users\equipo\Desktop\ml-extractor\frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

**Result:** 
- ✅ Frontend: http://localhost:3002
- ✅ Backend API: http://localhost:8009
- ✅ Auto-refresh on code changes

### 🔧 Method 2: Legacy Flask App (Backup)

If the FastAPI setup has issues, you can use the legacy Flask app:

```powershell
# In PowerShell
cd c:\Users\equipo\Desktop\ml-extractor

# Activate Python environment
.\.venv\Scripts\activate

# Run the Flask app
python app_improved.py
```

**Result:**
- ✅ Full app: http://localhost:5000
- ✅ Includes file upload and processing

### 🔧 Method 3: Simple Flask Fallback

For basic testing:

```powershell
# In PowerShell
cd c:\Users\equipo\Desktop\ml-extractor

# Run simple Flask app
python app_flask.py
```

**Result:**
- ✅ Basic app: http://localhost:5000
- ✅ Core functionality only

## 🎯 Testing the UI Features

### Frontend Testing (React - Port 3002)
1. **File Upload**: Drag & drop Excel/CSV files
2. **ML Template Analysis**: Upload ML template files
3. **Product Data Analysis**: Upload product data
4. **Mapping Configuration**: Configure field mappings
5. **ML File Generation**: Generate Mercado Libre files

### Backend API Testing (FastAPI - Port 8009)
1. **API Docs**: http://localhost:8009/docs
2. **Health Check**: http://localhost:8009/health
3. **File Upload**: POST /api/files/upload
4. **ML Processing**: POST /api/ml/process

## 🛠️ Development Commands

### Frontend Development
```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run linting
npm run lint

# Format code
npm run format
```

### Backend Development
```powershell
# Navigate to backend
cd backend

# Start with auto-reload
python -m uvicorn main:app --reload --port 8009

# Start with specific host
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8009

# Run with debug logging
python -m uvicorn main:app --reload --port 8009 --log-level debug
```

## 🔍 Troubleshooting

### Port Conflicts
If ports are busy:
```powershell
# Check what's using port 3002
netstat -ano | findstr :3002

# Check what's using port 8009
netstat -ano | findstr :8009

# Kill process by PID
taskkill /PID [PID_NUMBER] /F
```

### Frontend Issues
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Backend Issues
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Database Issues
```powershell
# Reset database
Remove-Item backend\ml_extractor.db
cd backend
python -c "from database import create_tables; create_tables()"
```

## 🌐 Testing URLs

### React Frontend (Development)
- **Main App**: http://localhost:3002
- **File Upload**: http://localhost:3002/upload
- **Mapping**: http://localhost:3002/mapping
- **Dashboard**: http://localhost:3002/dashboard

### FastAPI Backend (API)
- **API Documentation**: http://localhost:8009/docs
- **Alternative Docs**: http://localhost:8009/redoc
- **Health Check**: http://localhost:8009/health
- **API Status**: http://localhost:8009/api/status

### Legacy Flask App (Fallback)
- **Main App**: http://localhost:5000
- **All Features**: Integrated in single app

## 📱 Mobile Testing

The React frontend is responsive and can be tested on mobile:

```powershell
# Get your computer's IP
ipconfig

# Access from mobile device
# Frontend: http://[YOUR_IP]:3002
# Backend: http://[YOUR_IP]:8009
```

## 🔧 Environment Configuration

### Development Environment Variables
Create `backend/.env` for local development:
```bash
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3002,http://localhost:3000
DATABASE_URL=sqlite:///./ml_extractor.db
```

### Frontend Proxy Configuration
The frontend `package.json` is configured to proxy API requests:
```json
"proxy": "http://localhost:8009"
```

This means API calls from React will automatically forward to the FastAPI backend.

## 🎯 Recommended Development Workflow

1. **Start Backend First**:
   ```powershell
   cd backend
   python -m uvicorn main:app --reload --port 8009
   ```

2. **Start Frontend Second**:
   ```powershell
   cd frontend
   npm start
   ```

3. **Open Browser**:
   - Frontend: http://localhost:3002
   - API Docs: http://localhost:8009/docs

4. **Test Features**:
   - Upload files through React UI
   - Check API responses in browser dev tools
   - Test file processing workflows

## ✅ Success Indicators

When everything is working correctly:
- ✅ React app loads at localhost:3002
- ✅ No console errors in browser
- ✅ API calls succeed (check Network tab in DevTools)
- ✅ File uploads work
- ✅ Backend responds at localhost:8009/docs

**Ready to test! Start with Method 1 for the full experience.** 🚀
