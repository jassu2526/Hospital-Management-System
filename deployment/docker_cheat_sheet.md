# Docker Cheat Sheet for HMS Project

## Startup & Teardown

**Start all services in detached mode (background):**
```bash
docker-compose up -d
```

**View live logs of all services:**
```bash
docker-compose logs -f
```

**View logs of a specific service:**
```bash
docker-compose logs -f backend
# or frontend, db
```

**Stop all services:**
```bash
docker-compose down
```

**Stop all services AND remove volumes (resets database!):**
```bash
docker-compose down -v
```

## Rebuilding

**Rebuild images if you modified Dockerfile or requirements.txt/package.json:**
```bash
docker-compose up -d --build
```

**Rebuild a specific service:**
```bash
docker-compose up -d --build frontend
```

## Running Commands Inside Containers

**Run Django migrations:**
```bash
docker-compose exec backend python manage.py migrate
```

**Create a Django superuser:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Open a bash shell inside the backend container:**
```bash
docker-compose exec backend bash
```

**Open a psql shell in the database container:**
```bash
docker-compose exec db psql -U myuser -d mydb
```

## Troubleshooting

**Check if containers are running:**
```bash
docker-compose ps
```

**Check resource usage of containers:**
```bash
docker stats
```
