# Deployment Guide

## Quick Start (Local Docker)

```bash
cd retro-board
docker-compose up --build
```

Open http://localhost in your browser.

---

## Deployment Options with Public IP

### Option 1: DigitalOcean Droplet (Recommended)
**Cost:** $6/month | **Static IP:** Yes | **Complexity:** Medium

1. Create a Droplet (Ubuntu 24.04, Basic, $6/mo)
2. Note the public IP address
3. SSH into the droplet:
   ```bash
   ssh root@YOUR_IP
   ```

4. Install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```

5. Clone and deploy:
   ```bash
   git clone YOUR_REPO_URL retro-board
   cd retro-board
   docker-compose up -d --build
   ```

6. Access at `http://YOUR_IP`

**Add SSL (optional):**
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

### Option 2: Fly.io (Easiest)
**Cost:** Free tier available | **Static IP:** $2/mo add-on | **Complexity:** Low

1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Login and launch:
   ```bash
   fly auth login
   cd retro-board
   fly launch
   ```

3. Create `fly.toml`:
   ```toml
   app = "retro-board"
   primary_region = "gru"  # São Paulo

   [build]

   [http_service]
     internal_port = 80
     force_https = true

   [mounts]
     source = "retro_data"
     destination = "/data"
   ```

4. Deploy:
   ```bash
   fly deploy
   ```

5. For static IP:
   ```bash
   fly ips allocate-v4
   ```

---

### Option 3: Railway (Simplest)
**Cost:** $5/mo | **Static IP:** No (use custom domain) | **Complexity:** Very Low

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Dockerfile and deploys
5. Add custom domain in settings

---

### Option 4: AWS EC2
**Cost:** ~$8/month (t3.micro) | **Static IP:** Yes (Elastic IP) | **Complexity:** High

1. Launch EC2 instance (Ubuntu, t3.micro)
2. Allocate Elastic IP and associate with instance
3. Configure Security Group:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
4. SSH and install Docker (same as DigitalOcean)
5. Deploy with docker-compose

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite connection string | `sqlite+aiosqlite:///./retro.db` |
| `CORS_ORIGINS` | JSON array of allowed origins | `["http://localhost:5173"]` |

Example `.env`:
```
DATABASE_URL=sqlite+aiosqlite:////data/retro.db
CORS_ORIGINS=["https://retro.yourdomain.com"]
```

---

## Production Checklist

- [ ] Set up SSL/HTTPS (Let's Encrypt)
- [ ] Configure firewall (ufw)
- [ ] Set up automatic backups for `/data` volume
- [ ] Add monitoring (Uptime Robot, Fly.io metrics)
- [ ] Configure log rotation

---

## Recommended: DigitalOcean One-Click Deploy

For the simplest setup with a static IP:

```bash
# On your local machine
export DROPLET_IP=your.droplet.ip

# Copy files to server
scp -r retro-board root@$DROPLET_IP:/opt/

# SSH and start
ssh root@$DROPLET_IP "cd /opt/retro-board && docker-compose up -d --build"
```

Your app will be live at `http://YOUR_DROPLET_IP`
