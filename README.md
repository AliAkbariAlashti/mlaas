# MLaaS Backend

Django REST backend for an e-commerce analytics service. Users authenticate with OTP, upload CSV or Excel data, map source columns, and run analytics asynchronously through Celery.

## MVP services

The service catalog is managed dynamically in Django Admin. Four services are active in the MVP:

- RFM customer segmentation
- Market Basket analysis using Apriori association rules
- Purchase Propensity scoring
- Sales Anomaly detection using Isolation Forest

The remaining six catalog services are available through the private-beta waitlist workflow.

## Stack

- Django and Django REST Framework
- PostgreSQL
- Redis
- Celery worker and Celery Beat
- Pandas, scikit-learn, and MLXtend
- Docker Compose

## Development running

### Docker Compose

Build and start Django, PostgreSQL, Redis, Celery, and Celery Beat:

```bash
docker compose up --build
```

The API is available at `http://localhost:8000/`, Swagger UI at `http://localhost:8000/api/docs/`, and the admin panel at `http://localhost:8000/admin/`.

Create an admin user in another terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

Run the tests:

```bash
docker compose exec web python manage.py test
```

Stop the development stack:

```bash
docker compose down
```

PostgreSQL, Redis, and uploaded media use named Docker volumes and remain available after the containers stop.

### Local Python

Python 3.12 or newer and a locally running Redis instance are required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

Start each process in a separate terminal from the activated virtual environment:

```bash
python manage.py runserver
```

```bash
CELERY_BROKER_URL=redis://localhost:6379/0 \
CELERY_RESULT_BACKEND=redis://localhost:6379/1 \
celery -A mlaas worker -l info
```

```bash
CELERY_BROKER_URL=redis://localhost:6379/0 \
CELERY_RESULT_BACKEND=redis://localhost:6379/1 \
celery -A mlaas beat -l info
```

Without PostgreSQL environment variables, local development uses SQLite. Set `OTP_CACHE_URL=redis://localhost:6379/2` for shared OTP storage across multiple web processes.

## MVP authentication

The temporary development OTP is `123456` and expires after 120 seconds. `apps.authentication.services.send_otp` contains the production replacement `TODO`.

## API routes

All project and analytics routes require `Authorization: Bearer <access_token>`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/schema/` | Download the OpenAPI schema |
| `GET` | `/api/docs/` | Open Swagger UI |
| `POST` | `/api/v1/auth/send-otp/` | Request OTP |
| `POST` | `/api/v1/auth/verify-otp/` | Verify OTP and receive JWT tokens |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh an access token |
| `PUT` | `/api/v1/user/profile/` | Complete the business profile |
| `GET` | `/api/v1/services/` | List the dynamic service catalog |
| `POST` | `/api/v1/projects/upload/` | Upload a file and detect columns |
| `POST` | `/api/v1/projects/{id}/start/` | Submit mappings and queue analysis |
| `GET` | `/api/v1/projects/{id}/status/` | Poll processing status |
| `GET` | `/api/v1/projects/{id}/rfm-results/` | Fetch RFM results |
| `GET` | `/api/v1/projects/{id}/basket-results/` | Fetch basket rules |
| `GET` | `/api/v1/projects/{id}/predictive-results/` | Fetch propensity or anomaly results |
| `POST` | `/api/v1/projects/{id}/join-waitlist/` | Register a private-beta lead |

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Development-only value | Django signing secret |
| `DJANGO_DEBUG` | `true` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `TIME_ZONE` | `Asia/Tehran` | Application time zone |
| `POSTGRES_DB` | Not set | Enables PostgreSQL when provided |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_HOST` | `db` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/1` | Celery result backend |
| `OTP_CACHE_URL` | Local-memory cache | Shared OTP cache |

## Data lifecycle

Uploaded `.csv`, `.xls`, and `.xlsx` files are stored under `media/uploads/`. Celery Beat permanently removes raw uploads after 48 hours while keeping project metadata and calculated results.

## Tests

Run all Django tests:

```bash
python manage.py test
```

Run the ML engine tests directly:

```bash
python -m unittest ml_engines.tests
```
