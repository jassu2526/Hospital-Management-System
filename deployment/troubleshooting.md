# Troubleshooting Guide

Common issues and solutions for the HMS Full-Stack Project.

## Docker Issues

### 1. `docker-compose up` fails with "port is already allocated"
**Problem:** Another service (like local PostgreSQL or another web server) is already using port `8000`, `5432`, or `5173`.
**Solution:** 
- Stop the local service using the port.
- Or, change the exposed port in `docker-compose.yml` (e.g., change `8000:8000` to `8001:8000`).

### 2. Frontend changes are not showing up (Hot Reload failing)
**Problem:** Docker volumes on Windows/macOS sometimes don't propagate file change events correctly to the container.
**Solution:** We have added `CHOKIDAR_USEPOLLING=true` in `docker-compose.yml`. If issues persist, completely rebuild the container: `docker-compose up -d --build frontend`.

### 3. Database connection fails
**Problem:** Backend container starts before the database container is fully ready to accept connections.
**Solution:** The backend might crash initially. Docker-compose will typically restart it if configured, but you can manually restart it: `docker-compose restart backend`.

## Django Backend Issues

### 1. "Relation does not exist" or Database Errors
**Problem:** Migrations haven't been applied to the database.
**Solution:** Run migrations inside the docker container:
`docker-compose exec backend python manage.py migrate`

### 2. CORS Errors in Browser Console
**Problem:** The frontend is trying to access the backend from a different origin, and the backend isn't allowing it.
**Solution:** Check `hms/settings.py` and ensure `CORS_ALLOW_ALL_ORIGINS = True` (for dev) or configure `CORS_ALLOWED_ORIGINS` correctly. Ensure you are accessing the API using the exact URL configured in the frontend's `.env`.

### 3. Static Files Not Loading (404 for CSS/JS)
**Problem:** Whitenoise or static file configuration is missing.
**Solution:** Make sure you ran `python manage.py collectstatic`. In Docker, this is done automatically if you add it to the startup script, but locally you must run it manually.

## React Frontend Issues

### 1. API Calls are failing / Network Error
**Problem:** The frontend is pointing to the wrong backend URL.
**Solution:** Check the `VITE_API_BASE_URL` in your `.env` file (or `.env.local`). It should be `http://localhost:8000` for local Docker development. Restart the frontend dev server after changing `.env` files.

### 2. Blank page on refresh
**Problem:** React Router needs all routes to serve `index.html`, but the static server is trying to find a directory matching the route.
**Solution:** This happens in production deployment. Ensure your hosting provider (like Render or Netlify) has a rewrite rule to redirect all paths (`/*`) to `index.html`.
