from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import TemplateResponse
from app.services import TemplateService

router = APIRouter()


@router.get("", response_model=list[TemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db)):
    service = TemplateService(db)
    templates = await service.get_all_templates()
    return templates
