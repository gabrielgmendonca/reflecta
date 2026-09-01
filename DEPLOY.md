# Deploying Reflecta to Render

Reflecta deploys to Render as three resources, all defined in [`render.yaml`](render.yaml):

| Resource | Type | URL |
|----------|------|-----|
| `reflecta-db` | PostgreSQL (free) | internal only |
| `reflecta-api` | Python web service | `https://reflecta-api.onrender.com` |
| `reflecta-web` | Static site | `https://reflecta-web.onrender.com` |

## Prerequisites

1. A [Render](https://render.com) account
2. This repository pushed to GitHub
3. Google OAuth credentials (optional — see [Google OAuth](#google-oauth) below)

## Deploy

1. In the Render Dashboard, click **New** > **Blueprint**
2. Connect this repository; Render detects `render.yaml`
3. Render prompts for the only two unset values:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

   Leave both blank to deploy without login, and add them later.
4. Click **Apply**

Everything else — the database connection string, `SECRET_KEY`, CORS origins,
and the frontend's API/WebSocket URLs — is wired automatically by the blueprint.

### Verify the service names

The blueprint hardcodes `https://reflecta-api.onrender.com` and
`https://reflecta-web.onrender.com` in the env vars. Render appends a random
suffix if a name is already taken globally. After the first deploy, confirm the
assigned URLs match; if either differs, update these five values and redeploy:

- `reflecta-api`: `CORS_ORIGINS`, `FRONTEND_URL`, `BACKEND_URL`
- `reflecta-web`: `VITE_API_URL`, `VITE_WS_URL`

## Environment variables

### Backend (`reflecta-api`)

| Variable | Set by | Notes |
|----------|--------|-------|
| `PYTHON_VERSION` | blueprint | `3.11.9`. Required — `requirements.txt` has no wheels for Render's default Python 3.14. |
| `DATABASE_URL` | blueprint | From `reflecta-db`. `postgresql://` is rewritten to `postgresql+asyncpg://` in `app/config.py`. |
| `SECRET_KEY` | blueprint | Generated once, then stable across deploys. |
| `CORS_ORIGINS` | blueprint | **Must be a JSON array**, e.g. `["https://reflecta-web.onrender.com"]`. |
| `FRONTEND_URL` | blueprint | Where `/api/auth/callback` redirects after login. |
| `BACKEND_URL` | blueprint | Builds the OAuth `redirect_uri` behind Render's proxy. |
| `GOOGLE_CLIENT_ID` | you | Blank disables login. |
| `GOOGLE_CLIENT_SECRET` | you | Blank disables login. |

### Frontend (`reflecta-web`)

| Variable | Value | Notes |
|----------|-------|-------|
| `NODE_VERSION` | `20.19.0` | Matches CI. |
| `VITE_API_URL` | `https://reflecta-api.onrender.com/api` | **The `/api` suffix is required.** `client.ts` uses this as a bare prefix (`${API_BASE}/boards`) and falls back to `/api` locally. Omitting it 404s every request. |
| `VITE_WS_URL` | `wss://reflecta-api.onrender.com` | **No path suffix.** `useWebSocket.ts` appends `/ws/{slug}` itself. |

Vite inlines these at *build* time, so changing either requires a redeploy of
the static site, not just a restart.

## Google OAuth

1. Open the [Google Cloud Console credentials page](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** of type **Web application**
3. Under **Authorized redirect URIs**, add exactly:

   ```
   https://reflecta-api.onrender.com/api/auth/callback
   ```

4. Copy the Client ID and Client Secret into the `reflecta-api` service's
   environment variables and redeploy.

The redirect URI must match `{BACKEND_URL}/api/auth/callback` character for
character, including the scheme and the absence of a trailing slash.

## Free tier caveats

- **Spin-down.** Free services sleep after 15 minutes of inactivity. The next
  request takes ~30s, and any open WebSocket is dropped — collaborators see a
  reconnect on the first visit after an idle period.
- **Database expiry.** Render's free PostgreSQL instances are deleted after 90
  days. For something longer-lived, point `DATABASE_URL` at a
  [Neon](https://neon.tech) database instead and remove the `databases:` block.

## Troubleshooting

**Build fails on `pydantic-core` / `asyncpg`** — `PYTHON_VERSION` is not being
applied. Confirm it is set to `3.11.9` on `reflecta-api`.

**Every API call 404s** — `VITE_API_URL` is missing the `/api` suffix.

**CORS errors** — `CORS_ORIGINS` must be a JSON array containing the frontend's
exact origin, with no trailing slash.

**WebSocket won't connect** — `VITE_WS_URL` must use `wss://` (not `https://`)
and must *not* include `/ws`.

**OAuth "redirect_uri_mismatch"** — the URI in Google Console does not match
`{BACKEND_URL}/api/auth/callback`.

**Neon connection errors** — Neon's connection strings include
`channel_binding` and `sslmode` parameters that asyncpg rejects; `app/config.py`
strips them automatically.
