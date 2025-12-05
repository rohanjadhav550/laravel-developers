# KB-Admin Docker Setup

## Architecture

KB-Admin runs as a **separate microservice** with its own docker-compose.yml file, sharing the `laravel-microservices` network with other services.

```
laravel-microservices network:
├── laravel-app-dev (port 8000)
├── idea-agent (port 8001)
├── kb-admin (port 8002)      ← This service
├── redis-vector-db (port 6379)
└── mysql (port 3306)
```

## Prerequisites

1. **Network must exist**: The `laravel-microservices` network should already be created by the main-app or idea-agent.

2. **Required services running**:
   - MySQL (from main-app)
   - Redis Stack (from idea-agent)

## Setup Options

### Option 1: Use Shared Redis & MySQL (Recommended)

This assumes Redis and MySQL are already running from other compose files.

```bash
# 1. Make sure the network exists
docker network ls | grep laravel-microservices

# If network doesn't exist, create it:
docker network create laravel-microservices

# 2. Start kb-admin service
cd kb-admin
docker-compose up -d kb-admin

# 3. Check logs
docker-compose logs -f kb-admin
```

**Expected output:**
```
✓ MySQL connection successful
✓ Redis connection successful
✓ kb-admin service started successfully on port 8000
```

### Option 2: Standalone Mode (For Development/Testing)

If you want to run kb-admin with its own Redis and MySQL instances:

```bash
cd kb-admin
docker-compose --profile standalone up -d
```

This will start:
- kb-admin service
- Redis Stack (standalone instance)
- MySQL (standalone instance)

**Note:** This creates separate data stores, not shared with other services.

## Starting All Services Together

If you want to start everything in the correct order:

```bash
# Terminal 1: Start main Laravel app (if not already running)
cd main-app
docker-compose up -d

# Terminal 2: Start idea-agent and Redis
cd idea-agent
docker-compose up -d

# Terminal 3: Start kb-admin
cd kb-admin
docker-compose up -d
```

## Verify Connection

```bash
# Check if kb-admin can reach MySQL
docker exec -it kb-admin python -c "from app.database import test_connection; print('MySQL:', test_connection())"

# Check if kb-admin can reach Redis
docker exec -it kb-admin python -c "from app.redis_client import test_redis_connection; print('Redis:', test_redis_connection())"

# Check network connectivity
docker exec -it kb-admin ping -c 2 redis-vector-db
docker exec -it kb-admin ping -c 2 mysql
```

## Run Migrations

```bash
# After kb-admin is running
docker exec -it kb-admin python migrations/run_migrations.py
```

Expected output:
```
Found 4 migration files
Running migration: 001_create_knowledge_bases_table.sql
✓ Migration 001_create_knowledge_bases_table.sql completed successfully
Running migration: 002_create_kb_documents_table.sql
✓ Migration 002_create_kb_documents_table.sql completed successfully
Running migration: 003_create_learned_knowledge_table.sql
✓ Migration 003_create_learned_knowledge_table.sql completed successfully
Running migration: 004_create_kb_audit_log_table.sql
✓ Migration 004_create_kb_audit_log_table.sql completed successfully
All migrations completed successfully!
```

## Access API

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/health

## Environment Variables

The kb-admin service uses these environment variables (configured in docker-compose.yml):

```yaml
REDIS_URL: redis://redis-vector-db:6379
DB_HOST: mysql
DB_USERNAME: root
DB_PASSWORD: rootsecret
DB_DATABASE: laravel
LARAVEL_API_URL: http://laravel-app-dev:8000
IDEA_AGENT_URL: http://idea-agent:8000
```

To override (for development):

```bash
# Create .env file
cp .env.example .env
# Edit .env with your values

# Restart service
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs kb-admin

# Common issues:
# 1. Network doesn't exist
docker network create laravel-microservices

# 2. MySQL not accessible
docker-compose ps  # Check if MySQL is running in main-app
docker exec -it kb-admin ping mysql

# 3. Redis not accessible
docker exec -it kb-admin ping redis-vector-db
```

### MySQL connection error

```bash
# Verify MySQL is running
docker ps | grep mysql

# Check credentials match
docker exec -it mysql mysql -u root -prootsecret -e "SELECT 1"

# Update docker-compose.yml if credentials are different
```

### Redis connection error

```bash
# Verify Redis Stack is running
docker ps | grep redis

# Test connection from kb-admin
docker exec -it kb-admin redis-cli -h redis-vector-db ping
# Should return: PONG
```

### Port 8002 already in use

```bash
# Find what's using the port
netstat -ano | findstr :8002  # Windows
lsof -i :8002                 # Linux/Mac

# Change port in docker-compose.yml
ports:
  - "8003:8000"  # Use different external port
```

## Stopping Services

```bash
# Stop kb-admin only
cd kb-admin
docker-compose down

# Stop kb-admin and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop all services
cd main-app && docker-compose down
cd idea-agent && docker-compose down
cd kb-admin && docker-compose down
```

## Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f kb-admin

# Restart service
docker-compose restart kb-admin

# Rebuild and start (after code changes)
docker-compose up -d --build

# Execute command inside container
docker-compose exec kb-admin python migrations/run_migrations.py

# Shell access
docker-compose exec kb-admin bash

# Stop services
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

## Network Diagram

```
┌─────────────────────────────────────────────────────────┐
│         Docker Network: laravel-microservices           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐     ┌──────────────┐                  │
│  │  Laravel App │     │  Idea Agent  │                  │
│  │  Port: 8000  │────▶│  Port: 8001  │                  │
│  └──────────────┘     └──────┬───────┘                  │
│         │                    │                           │
│         │                    ▼                           │
│         │            ┌──────────────┐                    │
│         │            │   KB-Admin   │  ← New Service    │
│         │            │  Port: 8002  │                    │
│         │            └──────┬───────┘                    │
│         │                   │                            │
│         ▼                   ▼                            │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │    MySQL     │◀───│ Redis Stack  │                   │
│  │  Port: 3306  │    │  Port: 6379  │                   │
│  └──────────────┘    └──────────────┘                   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Quick Commands Cheatsheet

```bash
# Start kb-admin
cd kb-admin && docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f kb-admin

# Run migrations
docker exec -it kb-admin python migrations/run_migrations.py

# Test API
curl http://localhost:8002/health

# Shell access
docker exec -it kb-admin bash

# Stop
docker-compose down
```

## Production Considerations

For production deployment:

1. **Remove volume mounts** (use image code, not local files)
2. **Use environment-specific .env files**
3. **Enable authentication** on API endpoints
4. **Configure proper CORS** origins (not `["*"]`)
5. **Use secrets management** for API keys
6. **Set up logging** to external service
7. **Configure resource limits** in docker-compose.yml
8. **Use production WSGI server** (Gunicorn instead of uvicorn)

Example production override:

```yaml
# docker-compose.prod.yml
services:
  kb-admin:
    volumes: []  # Remove volume mount
    environment:
      - DEBUG=False
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
