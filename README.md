# Hospital Management System (Django)

## Features
- Role-based dashboards: Admin, Doctor, Patient, Attendant
- Multi-hospital, rooms, shifts
- Appointment booking & approval with email notifications
- Real-time occupancy analytics with Chart.js
- REST API + JWT authentication

## Setup
1. Python 3.11+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Migrate:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create superuser:
   ```
   python manage.py createsuperuser
   ```
5. Run dev server:
   ```
   python manage.py runserver
   ```

## JWT
- Obtain: POST /api/token/ {username, password}
- Refresh: POST /api/token/refresh/

## API Endpoints
- GET /analytics/api/occupancy/
- GET/POST /appointments/api/patient/
- GET /appointments/api/doctor/
- PATCH /appointments/api/doctor/{id}/
- PUT /hospital/api/room/{id}/update/

## Notes
- Email backend uses console in development
- Static files served via Whitenoise

