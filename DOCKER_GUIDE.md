# Docker Deployment Guide

## Quick Start with Docker Compose

Run everything with a single command:

```bash
docker-compose up -d
```

This will:
1. Start SearXNG on port 8090
2. Start the Culinary Trend MCP Server on port 8091
3. Create persistent volumes for data

## Verify Services

Check if both services are running:

```bash
docker-compose ps
```

You should see:
```
NAME                        STATUS
searxng                     Up (healthy)
culinary-trend-mcp          Up (running)
```

## View Logs

Watch live logs:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f culinary-trend-mcp
docker-compose logs -f searxng
```

## Check SearXNG Health

```bash
curl http://localhost:8090/
```

Should return: `200 OK`

## Check MCP Server Health

```bash
curl -X POST http://localhost:8091/ \
  -H "Content-Type: application/json" \
  -d '{"method": "get_active_monitors", "params": {}}'
```

## Access Data

Database and logs are stored in Docker volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect culinary-trend-mcp_mcp_data
```

## Stop Services

```bash
# Stop but keep containers
docker-compose stop

# Remove containers and networks
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

## Hermes Integration via Docker

Configure Hermes to connect to the containerized MCP server:

```json
{
  "mcp_servers": {
    "culinary_trends": {
      "command": "curl",
      "args": ["-X", "POST", "http://localhost:8091/"],
      "env": {
        "SEARXNG_URL": "http://searxng:8080"
      }
    }
  }
}
```

Or use stdio mode in the MCP server container.

## Environment Variables

Modify in `docker-compose.yml`:

```yaml
environment:
  - SEARXNG_URL=http://searxng:8080     # Don't change (internal)
  - LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
  - DATABASE_PATH=/data/culinary_trends.db
```

## Persistence

All data is stored in Docker volumes:

- **searxng_data**: SearXNG configuration and cache
- **mcp_data**: Database, logs, and monitoring data

Data persists across container restarts.

## Development

To build and test locally:

```bash
# Build image
docker build -t culinary-trend-mcp:latest .

# Run with docker-compose
docker-compose up --build
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Verify SearXNG is ready
docker-compose exec searxng curl http://localhost:8080/
```

### Database locked

```bash
# Remove and restart
docker-compose down -v
docker-compose up -d
```

### Permission issues

```bash
# Fix volume permissions
docker-compose exec mcp chmod 755 /data
```

## Production Deployment

For production, consider:

1. Use environment file:
```bash
# Create .env
SEARXNG_URL=https://your-searxng-domain.com
LOG_LEVEL=WARNING

# Use in compose
docker-compose --env-file .env up -d
```

2. Add resource limits to `docker-compose.yml`:
```yaml
culinary-trend-mcp:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

3. Use reverse proxy (nginx):
```nginx
server {
    listen 80;
    server_name mcp.yourdomain.com;

    location / {
        proxy_pass http://localhost:8091/;
        proxy_set_header Host $host;
    }
}
```

## Networking

Services communicate via `culinary-network`:
- SearXNG: `http://searxng:8080` (internal)
- External: `http://localhost:8090` (external)

For external access:

```bash
# Get SearXNG IP
docker inspect culinary-trend-mcp_searxng_1 | grep IPAddress

# Access from host
curl http://localhost:8090/
```
