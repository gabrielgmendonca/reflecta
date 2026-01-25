# Combined Dockerfile for single-container deployment (Fly.io, Railway)
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Backend + Nginx
FROM python:3.11-slim

# Install nginx and supervisor
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt greenlet

# Copy backend code
COPY backend/app/ ./app/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# Nginx config
RUN rm /etc/nginx/sites-enabled/default
COPY <<'EOF' /etc/nginx/sites-enabled/retro-board
server {
    listen 80;
    server_name _;
    root /var/www/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
EOF

# Supervisor config to run both services
COPY <<'EOF' /etc/supervisor/conf.d/retro-board.conf
[supervisord]
nodaemon=true

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true

[program:uvicorn]
command=/usr/local/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
EOF

# Create data directory
RUN mkdir -p /data

ENV DATABASE_URL=sqlite+aiosqlite:////data/retro.db

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
