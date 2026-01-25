from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Template


DEFAULT_TEMPLATES = [
    {
        "name": "Start/Stop/Continue",
        "description": "Classic retrospective format focusing on what to start, stop, and continue doing.",
        "columns": [
            {"title": "Start", "color": "#22c55e"},
            {"title": "Stop", "color": "#ef4444"},
            {"title": "Continue", "color": "#3b82f6"},
        ],
    },
    {
        "name": "Mad/Sad/Glad",
        "description": "Focus on team emotions and feelings about the sprint.",
        "columns": [
            {"title": "Mad", "color": "#ef4444"},
            {"title": "Sad", "color": "#6366f1"},
            {"title": "Glad", "color": "#22c55e"},
        ],
    },
    {
        "name": "4Ls",
        "description": "Liked, Learned, Lacked, Longed For - comprehensive retrospective format.",
        "columns": [
            {"title": "Liked", "color": "#22c55e"},
            {"title": "Learned", "color": "#3b82f6"},
            {"title": "Lacked", "color": "#f97316"},
            {"title": "Longed For", "color": "#8b5cf6"},
        ],
    },
    {
        "name": "Sailboat",
        "description": "Visualize your team's journey with wind, anchors, rocks, and destination.",
        "columns": [
            {"title": "Wind (Helps)", "color": "#22c55e"},
            {"title": "Anchor (Slows)", "color": "#ef4444"},
            {"title": "Rocks (Risks)", "color": "#f97316"},
            {"title": "Island (Goals)", "color": "#3b82f6"},
        ],
    },
    {
        "name": "What Went Well / What Didn't",
        "description": "Simple two-column format for quick retrospectives.",
        "columns": [
            {"title": "What Went Well", "color": "#22c55e"},
            {"title": "What Didn't Go Well", "color": "#ef4444"},
        ],
    },
    {
        "name": "KALM",
        "description": "Keep, Add, Less, More - action-oriented retrospective.",
        "columns": [
            {"title": "Keep", "color": "#22c55e"},
            {"title": "Add", "color": "#3b82f6"},
            {"title": "Less", "color": "#f97316"},
            {"title": "More", "color": "#8b5cf6"},
        ],
    },
]


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_templates(self) -> list[Template]:
        stmt = select(Template)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_template(self, template_id: int) -> Template | None:
        return await self.db.get(Template, template_id)

    async def seed_templates(self):
        stmt = select(Template)
        result = await self.db.execute(stmt)
        existing = result.scalars().all()

        if not existing:
            for t in DEFAULT_TEMPLATES:
                template = Template(name=t["name"], description=t["description"], columns=t["columns"])
                self.db.add(template)
            await self.db.commit()
