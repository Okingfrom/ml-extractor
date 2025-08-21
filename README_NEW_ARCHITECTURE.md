# ML Extractor - React + FastAPI Architecture

## 🚀 Project Overview

ML Extractor has been completely refactored from a Flask+HTML application to a modern **React + Tailwind CSS + FastAPI** architecture. This new stack provides better performance, maintainability, and user experience while preserving all existing functionality.

## 📁 New Project Structure

```
ML EXTRACTOR/
├── frontend/                 # React application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── auth/        # Authentication components
│   │   │   ├── common/      # Shared components
│   │   │   ├── dashboard/   # Dashboard components
│   │   │   ├── files/       # File management components
│   │   │   └── mapping/     # Mapping configuration components
│   │   ├── contexts/        # React contexts (auth, theme)
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── styles/          # Tailwind CSS styles
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── tailwind.config.js
├── backend/                 # FastAPI application
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── files.py         # File processing endpoints
│   │   ├── mapping.py       # Mapping configuration endpoints
│   │   └── dashboard.py     # Dashboard and analytics endpoints
│   ├── core/                # Core configuration
│   │   ├── config.py        # Application settings
│   │   └── security.py      # Authentication & security
│   ├── models/              # Data models
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/            # Business logic services
│   │   ├── file_processor.py   # File processing service
│   │   └── ml_processor.py     # AI/ML enhancement service
│   ├── database.py          # Database configuration
│   ├── main.py              # FastAPI application entry point
│   └── requirements.txt     # Python dependencies
├── tests/                   # Test suites
│   ├── frontend/            # React component tests
│   └── backend/             # FastAPI endpoint tests
└── [legacy files...]       # Original Flask application (preserved)
```

## 🛠 Technology Stack

### Frontend
- **React 18.2.0** - Modern UI library with hooks
- **Tailwind CSS 3.3.6** - Utility-first CSS framework
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API communication
- **React Hot Toast** - Elegant notifications
- **Lucide React** - Beautiful icons
- **React Dropzone** - File upload with drag & drop

### Backend
- **FastAPI** - High-performance async Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL/SQLite** - Database options
- **JWT Authentication** - Secure token-based auth
- **OpenAI Integration** - AI-powered enhancements
- **Pandas** - Data manipulation and analysis
- **PyPDF2, openpyxl, python-docx** - File processing

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.8+
- PostgreSQL (optional, SQLite for development)

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:password@localhost/ml_extractor"
export OPENAI_API_KEY="your-openai-key"  # Optional for AI features

# Run development server
uvicorn main:app --reload

# Run with Python
python main.py
```

### Database Setup

```bash
# For PostgreSQL
createdb ml_extractor

# For development (SQLite)
export ENVIRONMENT=development
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
SECRET_KEY=your-secret-key-change-this-in-production
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://ml_extractor:password@localhost/ml_extractor

# File Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600  # 100MB

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
FRONTEND_URL=http://localhost:3000

# AI/OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

### Frontend Configuration

Update `src/services/config.js`:

```javascript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

## 📋 API Documentation

With the FastAPI backend running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify` - Email verification
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

#### File Management
- `POST /api/files/upload` - Upload file
- `GET /api/files/` - List user files
- `GET /api/files/{file_id}` - Get file details
- `POST /api/files/{file_id}/process` - Process file
- `GET /api/files/{file_id}/download` - Download file
- `DELETE /api/files/{file_id}` - Delete file

#### Mapping Configuration
- `POST /api/mapping/templates` - Create mapping template
- `GET /api/mapping/templates` - List templates
- `GET /api/mapping/templates/{id}` - Get template
- `PUT /api/mapping/templates/{id}` - Update template
- `DELETE /api/mapping/templates/{id}` - Delete template

#### Dashboard & Analytics
- `GET /api/dashboard/` - Dashboard data
- `GET /api/dashboard/analytics/files` - File analytics
- `GET /api/dashboard/analytics/templates` - Template analytics
- `GET /api/dashboard/analytics/performance` - Performance metrics

## 🎨 UI Components

### Authentication System
- **Login Page** - Secure JWT-based authentication
- **Register Page** - User registration with validation
- **Email Verification** - Account verification flow

### Dashboard
- **Statistics Overview** - File counts, processing stats, storage usage
- **Recent Files** - Quick access to recently uploaded files
- **Analytics Charts** - Visual data insights (ready for chart libraries)

### File Management
- **Drag & Drop Upload** - Modern file upload with progress
- **File List** - Paginated file management
- **Processing Status** - Real-time processing updates
- **Download Center** - Access to processed files

### Mapping Configuration
- **Visual Field Mapper** - Intuitive drag-and-drop field mapping
- **Template Manager** - Save and reuse mapping configurations
- **Validation System** - Real-time mapping validation
- **AI Suggestions** - Intelligent field mapping recommendations

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm test                    # Run all tests
npm run test:coverage      # Run with coverage
```

### Backend Tests
```bash
cd backend
pytest                     # Run all tests
pytest --cov=backend       # Run with coverage
pytest tests/backend/test_auth.py  # Run specific test file
```

## 🚀 Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy the 'build' folder to your static hosting service
```

### Backend Deployment

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using Heroku
```bash
# Create Procfile
echo "web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}" > Procfile

# Deploy
git add .
git commit -m "Deploy FastAPI app"
git push heroku main
```

## 🔄 Migration from Flask

### What's Preserved
- ✅ All file processing capabilities
- ✅ ML mapping functionality  
- ✅ User authentication and authorization
- ✅ File upload and download features
- ✅ Database schema (with improvements)
- ✅ AI enhancement features

### What's Improved
- 🚀 **Performance** - React SPA + FastAPI async processing
- 🎨 **UI/UX** - Modern, responsive design with Tailwind CSS
- 🛠 **Maintainability** - Component-based architecture
- 📱 **Mobile Experience** - Responsive design for all devices
- 🔐 **Security** - JWT tokens, proper CORS, input validation
- 📊 **Analytics** - Enhanced dashboard with detailed insights
- 🧪 **Testing** - Comprehensive test suites for frontend and backend

### Legacy Compatibility
The original Flask applications are preserved in the root directory and can still be used during the transition period.

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite** (`npm test` and `pytest`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## 📝 Development Workflow

### Adding New Features

1. **Backend API** - Add endpoint in `backend/api/`
2. **Database Model** - Update `backend/models/database.py`
3. **Pydantic Schema** - Update `backend/models/schemas.py`
4. **Service Logic** - Add business logic in `backend/services/`
5. **Frontend Service** - Add API calls in `frontend/src/services/`
6. **React Component** - Create UI components in `frontend/src/components/`
7. **Tests** - Add tests for both frontend and backend

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort + mypy
- **Commit Messages**: Conventional Commits format

## 🛠 Troubleshooting

### Common Issues

**Frontend won't start**
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

**Backend database errors**
```bash
# Reset database
export ENVIRONMENT=development  # Uses SQLite
python -c "from backend.database import create_tables; create_tables()"
```

**Import errors in backend**
```bash
# Make sure you're in the root directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**CORS errors**
- Check `ALLOWED_ORIGINS` in `backend/core/config.py`
- Ensure frontend URL is included in the list

## 🔮 Future Enhancements

- [ ] **Real-time Processing** - WebSocket integration for live updates
- [ ] **Advanced Analytics** - Chart.js/D3.js integration
- [ ] **Batch Processing** - Queue system with Celery/RQ
- [ ] **File Versioning** - Track file processing history
- [ ] **API Rate Limiting** - Redis-based rate limiting
- [ ] **Advanced AI Features** - Custom model integration
- [ ] **Multi-tenant Support** - Organization/team features
- [ ] **Advanced Export Options** - Multiple output formats

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test files for usage examples

---

**Built with ❤️ using React, Tailwind CSS, and FastAPI**
