# Retro Board

[![Backend CI](https://github.com/gabrielmendonca/retro-board/actions/workflows/backend.yml/badge.svg)](https://github.com/gabrielmendonca/retro-board/actions/workflows/backend.yml)
[![Frontend CI](https://github.com/gabrielmendonca/retro-board/actions/workflows/frontend.yml/badge.svg)](https://github.com/gabrielmendonca/retro-board/actions/workflows/frontend.yml)
[![Docker Build](https://github.com/gabrielmendonca/retro-board/actions/workflows/docker.yml/badge.svg)](https://github.com/gabrielmendonca/retro-board/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

A real-time collaborative retrospective tool with Python/FastAPI backend, React frontend, WebSocket sync, and SQLite storage.

## Features

- Boards with customizable columns
- Sticky note cards with drag-and-drop
- Real-time voting
- Card grouping
- Discussion timer
- Pre-built templates (Start/Stop/Continue, Mad/Sad/Glad, 4Ls, Sailboat, etc.)
- Export to PDF/CSV/JSON
- Real-time collaboration via WebSockets

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm

## Setup

### Backend

```bash
cd backend

# Create virtual environment (use Python 3.11 for best compatibility)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

1. Open http://localhost:5173 in your browser
2. Create a new board by entering a title and selecting a template
3. Share the board URL with your team
4. Add cards, vote, drag-and-drop to organize
5. Use the timer for timeboxed discussions
6. Export results in JSON, CSV, or PDF format

## API Endpoints

### REST API

- `POST /api/boards` - Create board (optionally from template)
- `GET /api/boards/{slug}` - Get full board state
- `PATCH /api/boards/{slug}` - Update board settings
- `POST /api/boards/{slug}/columns` - Create column
- `POST /api/boards/{slug}/columns/{id}/cards` - Create card
- `POST /api/boards/{slug}/cards/{id}/vote` - Toggle vote
- `POST /api/boards/{slug}/timer/start|stop|reset` - Timer control
- `GET /api/boards/{slug}/export/csv|pdf|json` - Export
- `GET /api/templates` - List templates

### WebSocket

Connect: `ws://localhost:8000/ws/{board_slug}?session_id={uuid}`

Events:
- `card:create`, `card:update`, `card:move`, `card:delete`
- `vote:toggle`
- `group:create`, `group:dissolve`
- `timer:start`, `timer:stop`, `timer:reset`

## Templates

- **Start/Stop/Continue** - Classic retrospective format
- **Mad/Sad/Glad** - Focus on team emotions
- **4Ls** - Liked, Learned, Lacked, Longed For
- **Sailboat** - Wind, Anchor, Rocks, Island metaphor
- **What Went Well / What Didn't** - Simple two-column format
- **KALM** - Keep, Add, Less, More

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy (async)
- SQLite with aiosqlite
- WebSockets
- ReportLab (PDF generation)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- @hello-pangea/dnd (drag-and-drop)
- Zustand (state management)
- Radix UI (accessible components)
- Lucide React (icons)
