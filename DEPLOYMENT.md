# Deploy MLaaS on an Ubuntu VM

This is the simplest production-style deployment for this repository. Docker Compose runs:

- Caddy for HTTPS and public traffic;
- the compiled React application through Nginx;
- Django and Gunicorn;
- PostgreSQL;
- Redis;
- Celery Worker and Celery Beat.

Only ports `80` and `443` are public. PostgreSQL, Redis, Django, and the frontend container remain inside the Docker network. Database data, uploaded files, generated reports, Redis data, and HTTPS certificates use persistent Docker volumes.

> **MVP warning:** OTP delivery still uses the development code `123456`. Deploy privately for demos and testing until a real SMS provider and OTP delivery are implemented in `apps/authentication/services.py`.

## 1. Prepare the VM and domain

Recommended starting VM:

- Ubuntu 24.04 LTS;
- 2 vCPU;
- 4 GB RAM;
- 25 GB disk.

Create an `A` record such as `ml.example.com` pointing to the VM public IP. Allow inbound TCP ports `22`, `80`, and `443`, plus UDP `443`, in the cloud firewall. Caddy needs the domain to resolve to the VM and ports 80/443 to be reachable before it can issue the HTTPS certificate.

## 2. Install Docker

Connect to the VM:

```bash
ssh ubuntu@YOUR_VM_IP
```

Install Docker from Docker's official Ubuntu repository:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

```bash
echo "Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc" | sudo tee /etc/apt/sources.list.d/docker.sources
```

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and reconnect so the Docker group applies:

```bash
exit
ssh ubuntu@YOUR_VM_IP
docker compose version
```

Official reference: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

## 3. Download the application

```bash
git clone https://github.com/AliAkbariAlashti/mlaas.git
cd mlaas
git switch feature/mlaas-mvp-platform
```

After the feature branch is merged, use `git switch main` instead.

## 4. Create production secrets

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Generate two random values:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

Edit the file:

```bash
nano .env.production
```

Set:

```dotenv
DOMAIN=ml.example.com
DJANGO_SECRET_KEY=PASTE_THE_FIRST_RANDOM_VALUE
POSTGRES_DB=mlaas
POSTGRES_USER=mlaas
POSTGRES_PASSWORD=PASTE_THE_SECOND_RANDOM_VALUE
TIME_ZONE=Asia/Tehran
```

Do not add `https://` to `DOMAIN`. Never commit `.env.production`; it is ignored by Git.

## 5. Start the platform

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

The first deployment builds the frontend and backend, creates PostgreSQL and Redis, applies Django migrations, collects static files, and requests the HTTPS certificate.

Check the services:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

All services should become `Up` or `healthy`. If they do not, inspect logs:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=200 web frontend caddy worker
```

## 6. Create the administrator

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Open:

- Website: `https://ml.example.com/`
- Dashboard: `https://ml.example.com/app/`
- Admin: `https://ml.example.com/admin/`
- API documentation: `https://ml.example.com/api/docs/`
- OpenAPI reference: `https://ml.example.com/api/reference/`

Replace `ml.example.com` with the configured domain.

## Deploy an update

From the project directory:

```bash
git pull --ff-only origin feature/mlaas-mvp-platform
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

Compose recreates changed application containers. Persistent volumes are not removed.

## Back up PostgreSQL and uploaded files

Create a backup directory and load the environment values:

```bash
mkdir -p backups
set -a
. ./.env.production
set +a
```

Database backup:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  > "backups/database-$(date +%F-%H%M).sql"
```

Uploaded files and generated reports backup:

```bash
docker run --rm \
  -v mlaas_media_data:/data:ro \
  -v "$PWD/backups":/backup \
  alpine tar czf "/backup/media-$(date +%F-%H%M).tar.gz" -C /data .
```

Copy the `backups/` directory to storage outside the VM.

## Useful commands

View live logs:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f web worker
```

Restart one service:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart worker
```

Run Django checks or tests:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec web python manage.py check --deploy
docker compose --env-file .env.production -f docker-compose.prod.yml exec web python manage.py test
```

Stop the application without deleting data:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml down
```

> Never add `--volumes` to `docker compose down` on the production VM. That option deletes PostgreSQL, uploads, and other persistent data.

## Common problems

### HTTPS certificate is not issued

- Confirm the domain `A` record resolves to the VM public IP.
- Confirm ports TCP 80/443 and UDP 443 are allowed by the cloud firewall.
- Run `docker compose --env-file .env.production -f docker-compose.prod.yml logs caddy`.

### Django reports `DisallowedHost`

Ensure `DOMAIN` contains only the hostname, then recreate the web service:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --force-recreate web
```

### Analysis stays in processing

Check Celery and Redis:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps worker redis
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=200 worker redis
```

### A deployment contains old code

Confirm the commit and force a rebuild:

```bash
git rev-parse --short HEAD
docker compose --env-file .env.production -f docker-compose.prod.yml build --no-cache web frontend worker beat
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```
