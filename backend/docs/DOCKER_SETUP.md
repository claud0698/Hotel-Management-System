# Docker Setup Guide - Phase 9

**Purpose**: Complete guide for containerizing and running the Hotel Management System with Docker

**Last Updated**: November 8, 2025

**Status**: Phase 9 - Ready for Review

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Concepts](#docker-concepts)
3. [Local Development with Docker](#local-development-with-docker)
4. [Docker Compose Setup](#docker-compose-setup)
5. [Building Docker Images](#building-docker-images)
6. [Running Containers](#running-containers)
7. [Multi-Container Workflows](#multi-container-workflows)
8. [Docker Best Practices](#docker-best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Run with Docker Compose (5 minutes)

```bash
cd backend

# Copy environment template
cp .env.example .env.local

# Start all services (API + PostgreSQL)
docker-compose up

# In another terminal, initialize database
docker-compose exec api python scripts/init_admin.py

# Test API
curl http://localhost:8001/health
```

### 2. Run Docker Image Directly (2 minutes)

```bash
# Build image
docker build -t hotel-api:latest .

# Run with external PostgreSQL
docker run -d \
  --name hotel-api \
  -p 8001:8001 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/hotel_dev \
  -e SECRET_KEY=your-secret-key \
  -e ENVIRONMENT=development \
  hotel-api:latest

# Check logs
docker logs hotel-api

# Stop container
docker stop hotel-api
```

---

## Docker Concepts

### What is Docker?

Docker is containerization technology that packages your application with all dependencies into a single unit that runs consistently everywhere.

**Key Benefits**:
- **Isolation**: App runs in isolated container
- **Reproducibility**: Same environment on dev, test, production
- **Portability**: Works on any machine with Docker
- **Scalability**: Easy to run multiple instances

### Dockerfile

The `Dockerfile` in backend/ defines how to build the container image.

**Current Dockerfile Structure**:
```dockerfile
FROM python:3.12-slim              # Base image
WORKDIR /app                       # Working directory
RUN apt-get install ...            # Install dependencies
COPY requirements.txt .            # Copy requirements
RUN pip install ...                # Install Python packages
COPY . .                           # Copy code
RUN useradd appuser                # Create non-root user
EXPOSE 8001                        # Expose port
HEALTHCHECK ...                    # Health check
CMD uvicorn app:app ...            # Start command
```

### Docker Images vs Containers

- **Image**: Blueprint (like a template)
  - Built from Dockerfile
  - Can be stored in registry (Docker Hub, GCR, ECR)
  - Immutable

- **Container**: Running instance of an image
  - Created from an image
  - Can be started/stopped/removed
  - Temporary (data persists if mounted)

---

## Local Development with Docker

### Setup

```bash
# 1. Ensure Docker is installed
docker --version
docker-compose --version

# 2. Build the image
cd backend
docker build -t hotel-api:dev .

# 3. Start PostgreSQL
docker run -d \
  --name postgres-dev \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=hotel_dev \
  -p 5432:5432 \
  postgres:15

# 4. Run API container
docker run -it \
  --name hotel-api-dev \
  -p 8001:8001 \
  -e DATABASE_URL=postgresql://postgres:password@postgres-dev:5432/hotel_dev \
  -e SECRET_KEY=dev-secret \
  -e ENVIRONMENT=development \
  --link postgres-dev \
  hotel-api:dev

# 5. In another terminal, initialize database
docker exec hotel-api-dev python scripts/init_admin.py

# 6. Test API
curl http://localhost:8001/health
```

### Development Workflow

```bash
# Watch for changes and rebuild
docker build -t hotel-api:dev . && docker restart hotel-api-dev

# View logs
docker logs -f hotel-api-dev

# Run commands in container
docker exec hotel-api-dev python scripts/check_indexes.py
docker exec hotel-api-dev pytest docs/testing/ -v

# Access container shell
docker exec -it hotel-api-dev /bin/bash

# Stop and remove
docker stop hotel-api-dev postgres-dev
docker rm hotel-api-dev postgres-dev
```

---

## Docker Compose Setup

### docker-compose.yml

Create `docker-compose.yml` in backend directory:

```yaml
version: '3.9'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: hotel-db
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
      POSTGRES_DB: ${DB_NAME:-hotel_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - hotel-network

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: hotel-api
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-password}@db:5432/${DB_NAME:-hotel_dev}
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-this}
      ENVIRONMENT: ${ENVIRONMENT:-development}
      DEBUG: ${DEBUG:-True}
      LOG_LEVEL: ${LOG_LEVEL:-DEBUG}
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000,http://localhost:5173}
    ports:
      - "8001:8001"
    volumes:
      - .:/app
      - /app/__pycache__
    command: >
      bash -c "
      alembic upgrade head &&
      python scripts/init_admin.py &&
      uvicorn app:app --host 0.0.0.0 --port 8001 --reload
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - hotel-network

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    container_name: hotel-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - hotel-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  hotel-network:
    driver: bridge
```

### .env.docker

Create `.env.docker` for Docker Compose:

```env
# Database
DB_USER=postgres
DB_PASSWORD=secure-password-change-this
DB_NAME=hotel_dev

# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Running with Docker Compose

```bash
# Start services in background
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f api

# View specific service logs
docker-compose logs db
docker-compose logs redis

# Stop services
docker-compose down

# Stop and remove volumes (clear database)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Run one-off command
docker-compose exec api python scripts/init_admin.py

# Access database
docker-compose exec db psql -U postgres -d hotel_dev

# Monitor services
docker-compose ps
```

---

## Building Docker Images

### Build Process

```bash
# Build with default tag
docker build -t hotel-api:latest .

# Build with multiple tags
docker build -t hotel-api:latest -t hotel-api:v1.0.0 .

# Build with build args
docker build \
  --build-arg PYTHON_VERSION=3.12 \
  -t hotel-api:latest .

# Build from specific Dockerfile
docker build -f Dockerfile.prod -t hotel-api:prod .

# Build without cache (clean build)
docker build --no-cache -t hotel-api:latest .
```

### Multi-Stage Build (Optimized)

The current Dockerfile uses multi-stage build:

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install /wheels/*
COPY . .
```

**Benefits**:
- Final image smaller (no build tools)
- Faster deployment
- Better security (no compilers in production)

### Building for Production

```bash
# Create optimized production image
docker build \
  --target runtime \
  --build-arg DEBUG=False \
  -t hotel-api:prod .

# Tag for registry
docker tag hotel-api:prod gcr.io/project/hotel-api:1.0.0

# Push to registry
docker push gcr.io/project/hotel-api:1.0.0
```

---

## Running Containers

### Basic Container Operations

```bash
# Run container
docker run -d \
  --name hotel-api \
  -p 8001:8001 \
  -e SECRET_KEY=your-key \
  hotel-api:latest

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs hotel-api
docker logs -f hotel-api  # Follow logs
docker logs --tail 100 hotel-api  # Last 100 lines

# Stop container
docker stop hotel-api

# Start stopped container
docker start hotel-api

# Remove container
docker rm hotel-api

# Remove image
docker rmi hotel-api:latest
```

### Environment Variables

```bash
# Pass environment variables
docker run -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-key \
  -e ENVIRONMENT=production \
  hotel-api:latest

# Load from .env file
docker run --env-file .env.production \
  hotel-api:latest

# View container environment
docker exec hotel-api env
```

### Volume Mounting

```bash
# Mount directory for development
docker run -v /path/to/backend:/app \
  hotel-api:latest

# Mount database directory
docker run -v postgres_data:/var/lib/postgresql/data \
  postgres:15

# Mount logs
docker run -v hotel_logs:/var/log/hotel-api \
  hotel-api:latest
```

### Port Mapping

```bash
# Map single port
docker run -p 8001:8001 hotel-api:latest

# Map multiple ports
docker run -p 8001:8001 -p 8002:8002 hotel-api:latest

# Map to random host port
docker run -p 8001 hotel-api:latest
docker port hotel-api  # See mapped port

# Map to specific host IP
docker run -p 192.168.1.100:8001:8001 hotel-api:latest
```

### Container Networking

```bash
# Create network
docker network create hotel-network

# Connect containers
docker run --network hotel-network \
  --name api \
  hotel-api:latest

docker run --network hotel-network \
  --name db \
  postgres:15

# In api container, connect to db
# DATABASE_URL=postgresql://db:5432/hotel_dev
```

---

## Multi-Container Workflows

### Development Stack

```bash
# Start all services
docker-compose up

# Initial setup
docker-compose exec api python scripts/init_admin.py

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests
docker-compose exec api pytest docs/testing/ -v

# View logs
docker-compose logs -f api

# Stop all
docker-compose down
```

### Testing Stack

```bash
# Start test services
docker-compose -f docker-compose.test.yml up

# Run tests
docker-compose -f docker-compose.test.yml exec api pytest docs/testing/ -v

# Generate coverage
docker-compose -f docker-compose.test.yml exec api pytest --cov=. --cov-report=html
```

### Debugging

```bash
# Enter container shell
docker-compose exec api /bin/bash

# Check database connection
docker-compose exec api python -c "
from database import SessionLocal
db = SessionLocal()
db.execute('SELECT 1')
print('Database connected!')
"

# Check environment
docker-compose exec api env

# View network info
docker network inspect hotel-network

# View volume info
docker volume inspect postgres_data
```

---

## Docker Best Practices

### 1. Use .dockerignore

Create `.dockerignore` in backend/:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env*
.git
.gitignore
.dockerignore
README.md
tests/
docs/
.pytest_cache
.coverage
*.db
.DS_Store
```

### 2. Security Best Practices

```dockerfile
# Use non-root user
RUN useradd -m appuser
USER appuser

# Use minimal base image
FROM python:3.12-slim

# Don't use latest tag in production
FROM python:3.12.0-slim

# Copy only necessary files
COPY --chown=appuser:appuser app.py .

# Run with --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt

# Don't store secrets in image
# Use environment variables or secrets management
```

### 3. Performance Best Practices

```dockerfile
# Order commands by change frequency
# Layers that change frequently at end
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # This layer will change often

# Use .dockerignore to exclude unnecessary files

# Multi-stage build for smaller images
FROM python:3.12 as builder
RUN pip wheel ...

FROM python:3.12-slim
COPY --from=builder /wheels /wheels

# Health checks
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8001/health
```

### 4. Development vs Production

**Development Dockerfile**:
```dockerfile
# Include dev tools
RUN pip install -r requirements-dev.txt

# Mount code as volume
# Use --reload flag
CMD uvicorn app:app --reload
```

**Production Dockerfile**:
```dockerfile
# Minimal dependencies
RUN pip install -r requirements.txt

# Copy code into image
COPY . .

# No reload, optimize for performance
CMD uvicorn app:app --workers 4
```

---

## Troubleshooting

### Issue: "Cannot connect to database"

```bash
# Check database container is running
docker-compose ps

# Check network connectivity
docker-compose exec api ping db

# Check DATABASE_URL
docker-compose exec api echo $DATABASE_URL

# View database logs
docker-compose logs db
```

### Issue: "Port already in use"

```bash
# Find what's using the port
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use different port
docker run -p 8002:8001 hotel-api:latest
```

### Issue: "Out of memory"

```bash
# Check container limits
docker stats

# Increase Docker memory limit
# Docker Desktop: Preferences → Resources → Memory

# Limit container memory
docker run -m 1g hotel-api:latest

# In docker-compose.yml
services:
  api:
    mem_limit: 1g
```

### Issue: "Permissions denied"

```bash
# Fix directory permissions
docker-compose exec api chown -R appuser:appuser /app

# Or in Dockerfile
RUN chown -R appuser:appuser /app
USER appuser

# Check file permissions
docker-compose exec api ls -la
```

### Issue: "Dependencies not installing"

```bash
# Clear cache and rebuild
docker build --no-cache -t hotel-api:latest .

# View build output
docker build --progress=plain -t hotel-api:latest .

# Check requirements.txt
docker-compose exec api pip list
```

---

## Docker Registry (Pushing Images)

### Push to Docker Hub

```bash
# Tag image
docker tag hotel-api:latest myusername/hotel-api:latest

# Login to Docker Hub
docker login

# Push
docker push myusername/hotel-api:latest

# Pull on another machine
docker pull myusername/hotel-api:latest
```

### Push to Google Container Registry (GCR)

```bash
# Configure gcloud
gcloud auth configure-docker

# Tag image
docker tag hotel-api:latest gcr.io/my-project/hotel-api:latest

# Push
docker push gcr.io/my-project/hotel-api:latest
```

### Push to Amazon ECR

```bash
# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag hotel-api:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/hotel-api:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/hotel-api:latest
```

---

## Summary

✅ **Docker Setup Complete**:
- Dockerfile for containerization
- docker-compose.yml for local development
- Multi-container stack (API + PostgreSQL + Redis)
- Best practices documentation
- Troubleshooting guide

**Next Steps** (Phase 9):
1. Review this guide
2. Test with docker-compose up
3. Create production deployment guide
4. Create production checklist

---

**Last Updated**: November 8, 2025
**Status**: Phase 9 - Ready for Review
