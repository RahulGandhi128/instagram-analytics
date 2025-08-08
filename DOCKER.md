# Docker Setup for Instagram Analytics

This guide will help you run the Instagram Analytics application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Git (to clone the repository)

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/RahulGandhi128/instagram-analytics.git
   cd instagram-analytics
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/health

## Docker Commands

### Production Mode
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart backend
docker-compose restart frontend
```

### Development Mode
```bash
# Run in development mode with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Only backend in development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up backend
```

### Individual Services
```bash
# Build and run only backend
docker-compose up backend --build

# Build and run only frontend
docker-compose up frontend --build

# Scale services (if needed)
docker-compose up --scale backend=2
```

## Container Management

### Viewing Container Status
```bash
# List running containers
docker-compose ps

# View container logs
docker-compose logs backend
docker-compose logs frontend

# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Database Access
```bash
# Access the SQLite database (if using default SQLite)
docker-compose exec backend python -c "
from models.database import db
from app import create_app
app = create_app()
with app.app_context():
    # Your database operations here
    pass
"
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI content generation

### Optional Variables
- `FLASK_ENV`: Set to 'development' for debug mode
- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `REACT_APP_API_URL`: Backend API URL for frontend

## Docker Configuration Files

### Main Files
- `docker-compose.yml`: Main configuration for production
- `docker-compose.dev.yml`: Development overrides
- `backend/Dockerfile`: Backend Python application
- `frontend/Dockerfile`: Frontend React application

### Configuration Files
- `.env.example`: Environment variables template
- `backend/.dockerignore`: Backend build exclusions
- `frontend/.dockerignore`: Frontend build exclusions
- `frontend/nginx.conf`: Nginx configuration for production

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "3001:3000"  # Frontend
     - "5001:5000"  # Backend
   ```

2. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Build Failures**:
   ```bash
   # Clean rebuild
   docker-compose down
   docker system prune -f
   docker-compose up --build --force-recreate
   ```

4. **Database Issues**:
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up --build
   ```

### Health Checks

Monitor service health:
```bash
# Check backend health
curl http://localhost:5000/health

# Check frontend
curl http://localhost:3000

# Container health status
docker-compose ps
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Specific container stats
docker stats instagram-analytics-backend
docker stats instagram-analytics-frontend
```

## Production Deployment

For production deployment:

1. **Use environment-specific configuration**:
   ```bash
   # Production environment file
   cp .env.example .env.production
   # Edit with production values
   ```

2. **Use production Docker Compose**:
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

3. **Set up reverse proxy** (recommended):
   - Use Nginx or Traefik as reverse proxy
   - Configure SSL certificates
   - Set up domain routing

4. **Monitor and backup**:
   - Set up log rotation
   - Configure database backups
   - Monitor container health

## Features Available

- ✅ AI Content Creation with OpenAI integration
- ✅ DALL-E 3 image generation
- ✅ Instagram analytics dashboard
- ✅ Indian calendar with holidays
- ✅ Chat interface with memory
- ✅ Analytics context integration
- ✅ Responsive design
- ✅ Health monitoring
- ✅ Hot reload in development

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure Docker and Docker Compose are updated
4. Check port availability
5. Review the troubleshooting section above
