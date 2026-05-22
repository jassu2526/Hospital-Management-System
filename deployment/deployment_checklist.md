# HMS Project Deployment Checklist

Use this checklist when preparing to deploy the Hospital Management System to a production environment.

## 1. Security & Configuration
- [ ] Set `DEBUG=False` in your production environment variables.
- [ ] Generate a strong, secure, and random `DJANGO_SECRET_KEY` and set it in environment variables.
- [ ] Configure `DJANGO_ALLOWED_HOSTS` to include only your production domain name (e.g., `api.myhms.com`).
- [ ] Set `CORS_ALLOW_ALL_ORIGINS=False` in production and define `CORS_ALLOWED_ORIGINS` to include only your frontend URL.
- [ ] Configure production database connection (PostgreSQL recommended over SQLite). Ensure `DATABASE_URL` is set correctly if using `dj_database_url`.

## 2. Static and Media Files
- [ ] Ensure Whitenoise is configured correctly to serve static files. (Already done in `settings.py`).
- [ ] If dealing with user-uploaded files (Media), configure cloud storage like AWS S3 using `django-storages`, as ephemeral disk space (like on Render) will be lost on restart.

## 3. Frontend Configuration
- [ ] Set `VITE_API_BASE_URL` in the frontend build environment to point to the production backend URL (e.g., `https://api.myhms.com`).
- [ ] Build the frontend using `npm run build` and ensure the `dist` folder is served by your static site host.
- [ ] If using a React Router SPA, configure your hosting provider to redirect all 404s to `index.html` (Rewrite rule: `/*` -> `/index.html`).

## 4. Email Services
- [ ] Configure a real SMTP backend in `settings.py` for production. Replace `django.core.mail.backends.console.EmailBackend` with `django.core.mail.backends.smtp.EmailBackend`.
- [ ] Provide `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `EMAIL_USE_TLS` in your `.env`.

## 5. Deployment Platform (e.g., Render)
- [ ] **Backend Service:** Connect your repository, set the Build Command to `./deployment/build.sh`, and the Start Command to `gunicorn hms.wsgi:application`.
- [ ] **Frontend Service:** Connect your repository, set the Build Command to `cd frontend && npm install && npm run build`, and publish directory to `frontend/dist`.
- [ ] **Database:** Provision a PostgreSQL database and provide the internal connection string to the Backend service.

## 6. Post-Deployment Verification
- [ ] Check deployment logs for any migration or build errors.
- [ ] Access the frontend URL and verify the UI loads.
- [ ] Test authentication (login/logout).
- [ ] Test API endpoints using the frontend or tools like Postman.
- [ ] Ensure static assets (CSS, JS, images) are loading properly.
