# Deployment Guide

This guide covers various deployment options for your AI Bot Builder platform.

## Quick Start (Local Development)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your settings

# 4. Run the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- Admin Dashboard: http://localhost:8000/admin
- API Docs: http://localhost:8000/docs

## Docker Deployment (Recommended)

### Option 1: Docker Compose (Easiest)

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your production settings

# 2. Start all services
docker-compose up -d

# 3. View logs
docker-compose logs -f app

# 4. Stop services
docker-compose down
```

This will start:
- API server on port 8000
- Qdrant (optional) on port 6333
- Redis (optional) on port 6379

### Option 2: Docker only (without Qdrant/Redis)

```bash
docker build -t ai-bot-builder .
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e ADMIN_PASSWORD=your-admin-password \
  -v $(pwd)/data:/app/data \
  ai-bot-builder
```

## Production Deployment

### 1. DigitalOcean App Platform

1. Fork/Push your code to GitHub
2. Go to DigitalOcean App Platform
3. Create New App → Select your repository
4. Configure:
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - **Port**: 8080
5. Add Environment Variables:
   - `SECRET_KEY`
   - `ADMIN_PASSWORD`
   - `DATABASE_URL` (use PostgreSQL addon)
   - `API_BASE_URL` (your app URL)
   - Add API keys as needed
6. Deploy!

Cost: ~$5-12/month

### 2. Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`
5. Add environment variables:
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set ADMIN_PASSWORD=your-password
   ```
6. Get your URL: `railway domain`

Cost: Free tier available, then usage-based

### 3. Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repository
4. Configure:
   - **Name**: ai-bot-builder
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Add environment variables (same as above)
6. Create Web Service

Cost: Free tier available

### 4. AWS EC2

```bash
# 1. SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu

# 3. Clone your repository
git clone your-repo-url
cd AI\ Bot\ Builder

# 4. Create .env file
nano .env
# Add your configuration

# 5. Start with Docker Compose
docker-compose up -d

# 6. (Optional) Set up Nginx reverse proxy
sudo apt install nginx -y
# Configure Nginx to proxy to port 8000
```

### 5. Heroku

```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create your-bot-builder-app

# 4. Add Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 5. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=your-password

# 6. Deploy
git push heroku main
```

Cost: $7+/month

## Database Options

### SQLite (Default - Good for small scale)
```env
DATABASE_URL=sqlite:///./data/botbuilder.db
```

### PostgreSQL (Recommended for production)
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Most cloud providers offer managed PostgreSQL:
- DigitalOcean: Managed Database
- Railway: PostgreSQL addon
- Render: PostgreSQL addon
- AWS: RDS
- Heroku: Heroku Postgres

## Qdrant Setup (for RAG)

### Option 1: Docker Compose (included)
Already configured in docker-compose.yml

### Option 2: Qdrant Cloud (Managed)
1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a cluster
3. Get your URL and API key
4. Add to .env:
```env
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key
```

### Option 3: Self-hosted
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

## SSL/HTTPS Setup

### With Nginx (recommended)

1. Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Configure Nginx:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Get SSL certificate:
```bash
sudo certbot --nginx -d yourdomain.com
```

### With Cloud Providers
Most platforms (Railway, Render, DigitalOcean App Platform) provide automatic SSL certificates.

## Environment Variables Reference

Required:
- `SECRET_KEY` - Random string for security
- `ADMIN_PASSWORD` - Admin dashboard password

Optional:
- `DATABASE_URL` - Database connection string
- `API_BASE_URL` - Your public URL
- `ALLOWED_ORIGINS` - CORS allowed origins
- `QDRANT_URL` - Qdrant server URL
- `QDRANT_API_KEY` - Qdrant API key
- `DEFAULT_ANTHROPIC_API_KEY` - Default Anthropic key
- `DEFAULT_OPENAI_API_KEY` - Default OpenAI key

## Monitoring and Logs

### View logs with Docker:
```bash
docker-compose logs -f app
```

### Set up log rotation:
```bash
# Add to /etc/logrotate.d/botbuilder
/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## Backup Strategy

### Database backup (SQLite):
```bash
# Backup
cp data/botbuilder.db data/botbuilder.db.backup

# Restore
cp data/botbuilder.db.backup data/botbuilder.db
```

### Database backup (PostgreSQL):
```bash
# Backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

## Scaling Tips

1. **Use PostgreSQL** instead of SQLite for production
2. **Enable Redis** for session management
3. **Set up load balancing** with multiple containers
4. **Use CDN** for static files
5. **Enable caching** for bot configurations
6. **Monitor API usage** and rate limit if needed

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Change default ADMIN_PASSWORD
- [ ] Use HTTPS in production
- [ ] Set strong API keys
- [ ] Enable CORS only for trusted domains
- [ ] Regularly update dependencies
- [ ] Set up firewall rules
- [ ] Monitor for suspicious activity
- [ ] Regular backups
- [ ] Keep Docker images updated

## Troubleshooting

### Database connection issues
```bash
# Check database file permissions
ls -la data/botbuilder.db

# Check if database is locked
lsof data/botbuilder.db
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View container logs
docker-compose logs -f
```

## Support

For issues and questions:
- Check the logs first
- Review the API docs at `/docs`
- Ensure all environment variables are set correctly
- Check database connectivity
