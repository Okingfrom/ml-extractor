# ML Extractor - Production Setup Guide

## 🚀 Production Deployment Checklist

### Pre-deployment
- [ ] Set `DEBUG=False` in environment variables
- [ ] Configure secure `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure Redis for caching/sessions
- [ ] Set proper `CORS_ORIGINS` for your domain
- [ ] Configure email settings (optional)
- [ ] Set up file storage with proper permissions
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up SSL certificates
- [ ] Configure backup strategy

### Security
- [ ] All sensitive data moved to environment variables
- [ ] No debug information exposed in production
- [ ] API rate limiting configured
- [ ] File upload size limits enforced
- [ ] Input validation on all endpoints
- [ ] SQL injection protection enabled
- [ ] XSS protection headers configured

### Performance
- [ ] Database indexes optimized
- [ ] Static files served by web server
- [ ] Compression enabled
- [ ] Caching strategy implemented
- [ ] File cleanup jobs scheduled
- [ ] Monitoring and logging configured

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# Required
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ORIGINS=https://yourdomain.com

# Optional
REDIS_URL=redis://localhost:6379/0
MAX_UPLOAD_SIZE=10485760
API_RATE_LIMIT=100
LOG_LEVEL=INFO
```

### Frontend Build

```bash
cd frontend
npm install
npm run build
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m alembic upgrade head  # Run database migrations
```

### Docker Deployment (Recommended)

```dockerfile
# Example Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY src/ ./src/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend
    location / {
        root /var/www/ml-extractor/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # File uploads (larger timeout)
    location /api/files/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        client_max_body_size 50M;
    }
}
```

### Monitoring

Set up monitoring for:
- Application uptime
- API response times
- Error rates
- Database performance
- Disk usage (uploads folder)
- Memory usage

### Backup Strategy

- **Database**: Daily automated backups
- **Uploaded files**: Regular backup to cloud storage
- **Configuration**: Version control all config files
- **Application**: Automated deployment with rollback capability

### Support

For production issues:
1. Check application logs: `/var/log/ml-extractor/app.log`
2. Verify environment variables are set correctly
3. Test database connectivity
4. Check file permissions on upload directory
5. Verify external API keys if using AI features

---
**Last updated**: August 22, 2025
