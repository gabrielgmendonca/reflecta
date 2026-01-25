import pytest
from httpx import AsyncClient


class TestBoardCRUD:
    """Test board create, read, update, delete operations."""

    async def test_create_board_with_default_columns(self, client: AsyncClient):
        response = await client.post(
            "/api/boards",
            json={"title": "Test Retro"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Retro"
        assert "slug" in data
        assert len(data["slug"]) == 8

    async def test_create_board_with_template(self, client: AsyncClient):
        response = await client.post(
            "/api/boards",
            json={"title": "Mad Sad Glad Retro", "template_id": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Mad Sad Glad Retro"

    async def test_get_board_by_slug(self, client: AsyncClient):
        # Create board first
        create_response = await client.post(
            "/api/boards",
            json={"title": "My Retro"}
        )
        slug = create_response.json()["slug"]

        # Get board
        response = await client.get(f"/api/boards/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Retro"
        assert data["slug"] == slug
        assert len(data["columns"]) == 3  # Default columns

    async def test_get_nonexistent_board(self, client: AsyncClient):
        response = await client.get("/api/boards/notfound")
        assert response.status_code == 404

    async def test_update_board_title(self, client: AsyncClient):
        # Create board
        create_response = await client.post(
            "/api/boards",
            json={"title": "Original Title"}
        )
        slug = create_response.json()["slug"]

        # Update board
        response = await client.patch(
            f"/api/boards/{slug}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    async def test_update_board_settings(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Settings Test"}
        )
        slug = create_response.json()["slug"]

        response = await client.patch(
            f"/api/boards/{slug}",
            json={
                "timer_duration": 600,
                "max_votes_per_user": 10,
                "allow_voting": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timer_duration"] == 600
        assert data["max_votes_per_user"] == 10
        assert data["allow_voting"] is False


class TestColumns:
    """Test column operations."""

    async def test_create_column(self, client: AsyncClient):
        # Create board
        create_response = await client.post(
            "/api/boards",
            json={"title": "Column Test"}
        )
        slug = create_response.json()["slug"]

        # Create column
        response = await client.post(
            f"/api/boards/{slug}/columns",
            json={"title": "New Column", "color": "#ff0000"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Column"
        assert data["color"] == "#ff0000"

    async def test_update_column(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Column Update Test"}
        )
        slug = create_response.json()["slug"]

        # Get board to find column ID
        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        # Update column
        response = await client.patch(
            f"/api/boards/{slug}/columns/{column_id}",
            json={"title": "Renamed Column", "color": "#00ff00"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Renamed Column"

    async def test_delete_column(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Column Delete Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        response = await client.delete(f"/api/boards/{slug}/columns/{column_id}")
        assert response.status_code == 200

        # Verify column is deleted
        board_after = await client.get(f"/api/boards/{slug}")
        assert len(board_after.json()["columns"]) == 2


class TestCards:
    """Test card operations."""

    async def test_create_card(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Card Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        response = await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Test card content",
                "color": "#fef08a",
                "session_id": session_id
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Test card content"
        assert data["vote_count"] == 0

    async def test_update_card(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Card Update Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        card_response = await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Original content",
                "color": "#fef08a",
                "session_id": session_id
            }
        )
        card_id = card_response.json()["id"]

        response = await client.patch(
            f"/api/boards/{slug}/cards/{card_id}",
            json={"content": "Updated content"}
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Updated content"

    async def test_delete_card(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Card Delete Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        card_response = await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Card to delete",
                "color": "#fef08a",
                "session_id": session_id
            }
        )
        card_id = card_response.json()["id"]

        response = await client.delete(f"/api/boards/{slug}/cards/{card_id}")
        assert response.status_code == 200

    async def test_move_card_between_columns(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Card Move Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        columns = board.json()["columns"]
        source_column_id = columns[0]["id"]
        target_column_id = columns[1]["id"]

        card_response = await client.post(
            f"/api/boards/{slug}/columns/{source_column_id}/cards",
            json={
                "content": "Card to move",
                "color": "#fef08a",
                "session_id": session_id
            }
        )
        card_id = card_response.json()["id"]

        response = await client.put(
            f"/api/boards/{slug}/cards/{card_id}/move",
            json={"column_id": target_column_id, "position": 0}
        )
        assert response.status_code == 200
        assert response.json()["column_id"] == target_column_id


class TestVoting:
    """Test voting functionality."""

    async def test_vote_on_card(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Voting Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        card_response = await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Vote on me",
                "color": "#fef08a",
                "session_id": session_id
            }
        )
        card_id = card_response.json()["id"]

        # Vote
        response = await client.post(
            f"/api/boards/{slug}/cards/{card_id}/vote",
            params={"session_id": session_id}
        )
        assert response.status_code == 200
        assert response.json()["voted"] is True
        assert response.json()["vote_count"] == 1

    async def test_unvote_on_card(self, client: AsyncClient):
        # Use a unique session ID for this test
        test_session = "unvote-test-session"

        create_response = await client.post(
            "/api/boards",
            json={"title": "Unvote Test"}
        )
        slug = create_response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        card_response = await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Toggle vote",
                "color": "#fef08a",
                "session_id": "card-owner"
            }
        )
        card_id = card_response.json()["id"]

        # Vote
        vote_response = await client.post(
            f"/api/boards/{slug}/cards/{card_id}/vote",
            params={"session_id": test_session}
        )
        assert vote_response.json()["voted"] is True
        assert vote_response.json()["vote_count"] == 1

        # Unvote (toggle)
        unvote_response = await client.post(
            f"/api/boards/{slug}/cards/{card_id}/vote",
            params={"session_id": test_session}
        )
        assert unvote_response.status_code == 200
        assert unvote_response.json()["voted"] is False
        # The vote_count in toggle response is fetched fresh
        assert unvote_response.json()["vote_count"] == 0

    async def test_max_votes_limit(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Max Votes Test"}
        )
        slug = create_response.json()["slug"]

        # Set max votes to 2
        await client.patch(
            f"/api/boards/{slug}",
            json={"max_votes_per_user": 2}
        )

        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]

        # Create 3 cards
        card_ids = []
        for i in range(3):
            card_response = await client.post(
                f"/api/boards/{slug}/columns/{column_id}/cards",
                json={
                    "content": f"Card {i}",
                    "color": "#fef08a",
                    "session_id": f"other-session-{i}"
                }
            )
            card_ids.append(card_response.json()["id"])

        # Vote on first two cards
        for card_id in card_ids[:2]:
            response = await client.post(
                f"/api/boards/{slug}/cards/{card_id}/vote",
                params={"session_id": session_id}
            )
            assert response.status_code == 200

        # Third vote should fail
        response = await client.post(
            f"/api/boards/{slug}/cards/{card_ids[2]}/vote",
            params={"session_id": session_id}
        )
        assert response.status_code == 400
        assert "Max votes" in response.json()["detail"]


class TestTimer:
    """Test timer functionality."""

    async def test_start_timer(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Timer Test"}
        )
        slug = create_response.json()["slug"]

        response = await client.post(f"/api/boards/{slug}/timer/start")
        assert response.status_code == 200
        assert response.json()["timer_end_time"] is not None

    async def test_stop_timer(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Timer Stop Test"}
        )
        slug = create_response.json()["slug"]

        await client.post(f"/api/boards/{slug}/timer/start")
        response = await client.post(f"/api/boards/{slug}/timer/stop")
        assert response.status_code == 200
        assert response.json()["timer_end_time"] is None

    async def test_reset_timer(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Timer Reset Test"}
        )
        slug = create_response.json()["slug"]

        await client.post(f"/api/boards/{slug}/timer/start")
        response = await client.post(f"/api/boards/{slug}/timer/reset")
        assert response.status_code == 200
        assert response.json()["timer_end_time"] is None


class TestTemplates:
    """Test template operations."""

    async def test_get_templates(self, client: AsyncClient):
        response = await client.get("/api/templates")
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) >= 5  # We seeded 5 templates
        assert templates[0]["name"] == "Start/Stop/Continue"

    async def test_board_uses_template_columns(self, client: AsyncClient):
        # Create board with Mad/Sad/Glad template (id=2)
        response = await client.post(
            "/api/boards",
            json={"title": "Template Board", "template_id": 2}
        )
        slug = response.json()["slug"]

        board = await client.get(f"/api/boards/{slug}")
        columns = board.json()["columns"]
        assert len(columns) == 3
        column_titles = [c["title"] for c in columns]
        assert "Mad" in column_titles
        assert "Sad" in column_titles
        assert "Glad" in column_titles


class TestExport:
    """Test export functionality."""

    async def test_export_json(self, client: AsyncClient, session_id: str):
        create_response = await client.post(
            "/api/boards",
            json={"title": "Export Test"}
        )
        slug = create_response.json()["slug"]

        # Add a card
        board = await client.get(f"/api/boards/{slug}")
        column_id = board.json()["columns"][0]["id"]
        await client.post(
            f"/api/boards/{slug}/columns/{column_id}/cards",
            json={
                "content": "Export this",
                "color": "#fef08a",
                "session_id": session_id
            }
        )

        response = await client.get(f"/api/boards/{slug}/export/json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    async def test_export_csv(self, client: AsyncClient):
        create_response = await client.post(
            "/api/boards",
            json={"title": "CSV Export Test"}
        )
        slug = create_response.json()["slug"]

        response = await client.get(f"/api/boards/{slug}/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
