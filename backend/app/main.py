from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db, async_session
from app.api import api_router
from app.websocket import manager, WebSocketHandler
from app.services import TemplateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Seed templates
    async with async_session() as db:
        template_service = TemplateService(db)
        await template_service.seed_templates()
    yield
    # Shutdown (nothing to do)


app = FastAPI(title="Retro Board API", lifespan=lifespan)

# Session middleware for OAuth state
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.websocket("/ws/{board_slug}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_slug: str,
    session_id: str,
):
    await manager.connect(websocket, board_slug, session_id)

    # Notify others that a user joined
    await manager.broadcast(
        board_slug,
        {"type": "user:joined", "payload": {"session_id": session_id}},
        exclude_session=session_id,
    )

    try:
        async with async_session() as db:
            handler = WebSocketHandler(db, manager, board_slug, session_id)

            while True:
                data = await websocket.receive_json()
                response = await handler.handle_message(data)
                if response:
                    await manager.send_personal(response, websocket)

    except WebSocketDisconnect:
        manager.disconnect(board_slug, session_id)
        await manager.broadcast(
            board_slug,
            {"type": "user:left", "payload": {"session_id": session_id}},
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
