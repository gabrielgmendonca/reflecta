# Deploying to Render

This guide explains how to deploy the Retro Board application to Render.

## Prerequisites

1. A [Render](https://render.com) account
2. A PostgreSQL database (Render provides one, or use an external service like Neon)
3. Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

## Quick Deploy (Blueprint)

The easiest way is to use the `render.yaml` blueprint:

1. Push your code to a GitHub/GitLab repository
2. In Render Dashboard, click **New** > **Blueprint**
3. Connect your repository
4. Render will detect `render.yaml` and create both services automatically
5. Configure environment variables (see below)

## Manual Deploy

### 1. Create PostgreSQL Database

If using Render's database:
1. Go to **New** > **PostgreSQL**
2. Choose the free tier
3. Copy the **Internal Database URL** for the backend

### 2. Deploy Backend (Web Service)

1. Go to **New** > **Web Service**
2. Connect your repository
3. Configure:
   - **Name**: `retro-board-api`
   - **Region**: Oregon (or your preference)
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Deploy Frontend (Static Site)

1. Go to **New** > **Static Site**
2. Connect the same repository
3. Configure:
   - **Name**: `retro-board-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `dist`

## Environment Variables

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | JWT signing key (auto-generated if using blueprint) | Random string |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["https://retro-board-frontend.onrender.com"]` |
| `FRONTEND_URL` | Frontend URL for OAuth redirects | `https://retro-board-frontend.onrender.com` |
| `BACKEND_URL` | Backend URL for OAuth callback | `https://retro-board-api.onrender.com` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Your secret |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://retro-board-api.onrender.com` |
| `VITE_WS_URL` | WebSocket URL | `wss://retro-board-api.onrender.com` |

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `https://retro-board-api.onrender.com/api/auth/callback`
4. Copy Client ID and Client Secret to backend environment variables

## Important Notes

- **Free tier**: Services spin down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds.
- **Database**: Render's free PostgreSQL databases expire after 90 days. Consider using [Neon](https://neon.tech) for a persistent free tier.
- **WebSocket**: Render supports WebSocket connections on web services.

## Troubleshooting

### Database Connection Issues

If using Neon or external PostgreSQL, the connection string may include parameters like `channel_binding=require` that aren't supported by asyncpg. The app automatically strips these parameters.

### CORS Errors

Ensure `CORS_ORIGINS` includes your frontend URL and is formatted as a JSON array:
```
["https://your-frontend.onrender.com"]
```

### OAuth Callback Errors

Verify that:
1. `BACKEND_URL` matches your Render backend URL exactly
2. The redirect URI in Google Console matches `{BACKEND_URL}/api/auth/callback`
3. `FRONTEND_URL` is set correctly for post-login redirects
