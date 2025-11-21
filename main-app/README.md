# Laravel React Application

A Laravel 12 application with Inertia.js, React 19, and Tailwind CSS v4.

## Prerequisites

- [Docker](https://www.docker.com/get-started) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd main-app
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Update `.env` for Docker:**
   ```env
   DB_CONNECTION=mysql
   DB_HOST=mysql
   DB_PORT=3306
   DB_DATABASE=laravel
   DB_USERNAME=laravel
   DB_PASSWORD=secret
   ```

## Running the Application

### Production Mode

Build and start the application:

```bash
docker-compose up --build
```

The application will be available at: **http://localhost:8080**

Run in detached mode:

```bash
docker-compose up -d --build
```

### Development Mode (with Hot Reload)

Start MySQL and the development server:

```bash
docker-compose --profile dev up mysql app-dev --build
```

- Application: **http://localhost:8000**
- Vite dev server: **http://localhost:5173**

## Post-Installation

After the containers are running, run migrations:

```bash
# Production
docker-compose exec app php artisan migrate

# Development
docker-compose exec app-dev php artisan migrate
```

Generate application key (if not set):

```bash
docker-compose exec app php artisan key:generate
```

## Common Commands

### Artisan Commands

```bash
# Run artisan commands
docker-compose exec app php artisan <command>

# Examples
docker-compose exec app php artisan migrate:fresh --seed
docker-compose exec app php artisan cache:clear
docker-compose exec app php artisan route:list
```

### Database Access

```bash
# Access MySQL CLI
docker-compose exec mysql mysql -u laravel -psecret laravel

# Database backup
docker-compose exec mysql mysqldump -u laravel -psecret laravel > backup.sql
```

### Container Management

```bash
# View logs
docker-compose logs -f app

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v

# Rebuild without cache
docker-compose build --no-cache
```

### Running Tests

```bash
docker-compose exec app php artisan test
```

## Database Configuration

| Setting | Value |
|---------|-------|
| Host | `mysql` |
| Port | `3306` |
| Database | `laravel` |
| Username | `laravel` |
| Password | `secret` |
| Root Password | `rootsecret` |

External access (from host machine): `localhost:3307`

## Troubleshooting

### Container won't start

Check if ports are already in use:
```bash
# Check port 8080
netstat -an | grep 8080

# Check port 3307
netstat -an | grep 3307
```

### Database connection refused

Wait for MySQL to be healthy before running migrations:
```bash
docker-compose ps
```

The `mysql` service should show `healthy` status.

### Permission issues

If you encounter permission errors:
```bash
docker-compose exec app chown -R www-data:www-data /var/www/html/storage
docker-compose exec app chmod -R 775 /var/www/html/storage
```

### Clear all caches

```bash
docker-compose exec app php artisan optimize:clear
```

## Project Structure

```
├── app/                  # Application code
├── bootstrap/            # Framework bootstrap
├── config/               # Configuration files
├── database/             # Migrations and seeders
├── docker/               # Docker configuration files
│   ├── nginx.conf        # Nginx configuration
│   └── supervisord.conf  # Supervisor configuration
├── public/               # Public assets
├── resources/            # Frontend resources (React, CSS)
├── routes/               # Route definitions
├── storage/              # Storage (logs, cache)
├── tests/                # Test files
├── Dockerfile            # Production Dockerfile
├── Dockerfile.dev        # Development Dockerfile
└── docker-compose.yml    # Docker Compose configuration
```
