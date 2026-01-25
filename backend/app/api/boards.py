from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import (
    BoardCreate, BoardUpdate, BoardResponse, BoardFullResponse,
    ColumnCreate, ColumnUpdate, ColumnResponse,
    CardCreate, CardUpdate, CardMove, CardResponse,
    CardGroupCreate, CardGroupUpdate, CardGroupResponse,
)
from app.services import BoardService, ExportService
from app.api.deps import get_current_user_optional, get_current_user

router = APIRouter()


@router.post("", response_model=BoardResponse)
async def create_board(
    data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    service = BoardService(db)
    owner_id = current_user.id if current_user else None
    board = await service.create_board(data.title, data.template_id, owner_id)
    return board


@router.get("/my", response_model=list[BoardResponse])
async def get_my_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BoardService(db)
    boards = await service.get_boards_by_owner(current_user.id)
    return boards


@router.get("/{slug}", response_model=BoardFullResponse)
async def get_board(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Manually construct response with vote counts
    columns_data = []
    for col in board.columns:
        cards_data = []
        for card in col.cards:
            cards_data.append(CardResponse.from_orm_with_votes(card))

        groups_data = [CardGroupResponse.model_validate(g) for g in col.groups]
        columns_data.append(ColumnResponse(
            id=col.id,
            board_id=col.board_id,
            title=col.title,
            color=col.color,
            position=col.position,
            cards=cards_data,
            groups=groups_data,
        ))

    return BoardFullResponse(
        id=board.id,
        slug=board.slug,
        title=board.title,
        owner_id=board.owner_id,
        timer_duration=board.timer_duration,
        timer_end_time=board.timer_end_time,
        allow_voting=board.allow_voting,
        max_votes_per_user=board.max_votes_per_user,
        created_at=board.created_at,
        columns=columns_data,
    )


@router.patch("/{slug}", response_model=BoardResponse)
async def update_board(slug: str, data: BoardUpdate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.update_board(slug, **data.model_dump(exclude_unset=True))
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.delete("/{slug}")
async def delete_board(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this board")
    success = await service.delete_board(slug)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete board")
    return {"success": True}


# Columns
@router.post("/{slug}/columns", response_model=ColumnResponse)
async def create_column(slug: str, data: ColumnCreate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    column = await service.create_column(board.id, data.title, data.color, data.position)
    return ColumnResponse(
        id=column.id,
        board_id=column.board_id,
        title=column.title,
        color=column.color,
        position=column.position,
        cards=[],
        groups=[],
    )


@router.patch("/{slug}/columns/{column_id}", response_model=ColumnResponse)
async def update_column(slug: str, column_id: int, data: ColumnUpdate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    column = await service.update_column(column_id, **data.model_dump(exclude_unset=True))
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return ColumnResponse(
        id=column.id,
        board_id=column.board_id,
        title=column.title,
        color=column.color,
        position=column.position,
        cards=[],
        groups=[],
    )


@router.delete("/{slug}/columns/{column_id}")
async def delete_column(slug: str, column_id: int, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    success = await service.delete_column(column_id)
    if not success:
        raise HTTPException(status_code=404, detail="Column not found")
    return {"success": True}


# Cards
@router.post("/{slug}/columns/{column_id}/cards", response_model=CardResponse)
async def create_card(slug: str, column_id: int, data: CardCreate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    card = await service.create_card(column_id, data.content, data.color, data.session_id)
    return CardResponse.from_orm_with_votes(card)


@router.patch("/{slug}/cards/{card_id}", response_model=CardResponse)
async def update_card(slug: str, card_id: int, data: CardUpdate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    card = await service.update_card(card_id, **data.model_dump(exclude_unset=True))
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardResponse.from_orm_with_votes(card)


@router.put("/{slug}/cards/{card_id}/move", response_model=CardResponse)
async def move_card(slug: str, card_id: int, data: CardMove, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    card = await service.move_card(card_id, data.column_id, data.position, data.group_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardResponse.from_orm_with_votes(card)


@router.delete("/{slug}/cards/{card_id}")
async def delete_card(slug: str, card_id: int, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    success = await service.delete_card(card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"success": True}


# Voting
@router.post("/{slug}/cards/{card_id}/vote")
async def toggle_vote(slug: str, card_id: int, session_id: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    result = await service.toggle_vote(card_id, session_id, slug)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Vote failed"))

    card = await service.get_card_with_votes(card_id)
    return {
        "success": True,
        "voted": result["voted"],
        "vote_count": len(card.votes) if card else 0,
    }


# Groups
@router.post("/{slug}/groups", response_model=CardGroupResponse)
async def create_group(slug: str, data: CardGroupCreate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    group = await service.create_group(board.id, data.column_id, data.title)
    return group


@router.patch("/{slug}/groups/{group_id}", response_model=CardGroupResponse)
async def update_group(slug: str, group_id: int, data: CardGroupUpdate, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    group = await service.update_group(group_id, **data.model_dump(exclude_unset=True))
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.delete("/{slug}/groups/{group_id}")
async def dissolve_group(slug: str, group_id: int, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    success = await service.dissolve_group(group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"success": True}


# Timer
@router.post("/{slug}/timer/start", response_model=BoardResponse)
async def start_timer(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.start_timer(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("/{slug}/timer/stop", response_model=BoardResponse)
async def stop_timer(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.stop_timer(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("/{slug}/timer/reset", response_model=BoardResponse)
async def reset_timer(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.reset_timer(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


# Export
@router.get("/{slug}/export/json")
async def export_json(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    content = ExportService.export_json(board)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={slug}.json"},
    )


@router.get("/{slug}/export/csv")
async def export_csv(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    content = ExportService.export_csv(board)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={slug}.csv"},
    )


@router.get("/{slug}/export/pdf")
async def export_pdf(slug: str, db: AsyncSession = Depends(get_db)):
    service = BoardService(db)
    board = await service.get_board_by_slug(slug)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    content = ExportService.export_pdf(board)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={slug}.pdf"},
    )
