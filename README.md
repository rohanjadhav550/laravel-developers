# Laravel Developer - Microservices Architecture

This project uses a microservices architecture where `main-app` serves as the anchor point with shared infrastructure, and additional microservices can be started/stopped on demand.

## Architecture Overview

```
laravel-developer/
├── main-app/              # Anchor service (Laravel app + MySQL + Network)
│   └── docker-compose.yml
└── idea-agent/            # Microservice (Python AI agent)
    └── docker-compose.yml
```

## Getting Started

### 1. Start the Anchor Service (Required)

The main-app creates the shared network and database:

```powershell
cd main-app
docker-compose up -d
```

This starts:
- Laravel application (port 8080)
- MySQL database
- Shared network: `laravel-microservices`

### 2. Start Microservices (Optional, On-Demand)

#### Idea Agent Microservice

```powershell
cd idea-agent
docker-compose up -d
```

Access at: `http://localhost:8001/`

## Managing Services

### Start a Microservice
```powershell
cd <service-name>
docker-compose up -d
```

### Stop a Microservice
```powershell
cd <service-name>
docker-compose down
```

### View Running Services
```powershell
docker ps
```

### View Logs
```powershell
cd <service-name>
docker-compose logs -f
```

## Inter-Service Communication

Services communicate via the `laravel-microservices` network using container names:

- From main-app to idea-agent: `http://idea-agent:8000/`
- From idea-agent to main-app: `http://laravel-app/`

## Development Mode

For development with hot-reload:

```powershell
cd main-app
docker-compose --profile dev up -d
```

This starts the dev server on ports 8000 (Laravel) and 5173 (Vite).

## Adding New Microservices

1. Create a new directory for your service
2. Create a `docker-compose.yml` with:
   ```yaml
   networks:
     laravel-microservices:
       external: true
       name: laravel-microservices
   ```
3. Ensure services connect to the `laravel-microservices` network
4. Start independently with `docker-compose up -d`

## Notes

- Always start `main-app` first (it creates the network)
- Microservices can be started/stopped independently
- All services share the same Docker network for communication
