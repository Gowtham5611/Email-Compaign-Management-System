# Production Deployment Guide

## Docker Compose Deployment (Recommended)

1. Clone repository to production server.
2. Copy environment file template:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` to set strong production secrets:
   ```env
   SECRET_KEY=generate-a-strong-random-32-character-secret
   DATABASE_URL=postgresql://postgres:postgrespassword@postgres:5432/email_sender
   REDIS_URL=redis://redis:6379/0
   ```
4. Build and start all services with Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
5. Verify container health:
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```
6. Access the application on `http://<your-server-ip>` (Port 80).

## Cloud Platform Deployment (AWS / GCP / DigitalOcean)
- **Database**: Managed PostgreSQL (AWS RDS / GCP Cloud SQL).
- **Redis**: Managed ElastiCache or Redis Cloud.
- **Backend API**: AWS ECS / Kubernetes / App Runner / DigitalOcean App Platform.
- **Frontend SPA**: AWS CloudFront + S3, Cloudflare Pages, or Vercel.

