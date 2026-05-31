"""
Unit tests for NudgeService — proactive employee reminders.
"""

import pytest
from app.services.nudge_service import NudgeService


USER_X = "xxxx-xxxx-xxxx-xxxx"
USER_Y = "yyyy-yyyy-yyyy-yyyy"


@pytest.fixture
def service():
    """Fresh NudgeService with clean nudge list per test."""
    from app.services import nudge_service as ns_module
    ns_module._nudges.clear()
    svc = NudgeService()
    return svc


class TestNudgeService:
    @pytest.mark.asyncio
    async def test_create_nudge(self, service):
        nudge = await service.create_nudge(
            user_id=USER_X,
            nudge_type="leave_reminder",
            title="Cuti Banyak!",
            content="Kau ada 12 hari cuti lagi!"
        )
        assert nudge["user_id"] == USER_X
        assert nudge["type"] == "leave_reminder"
        assert nudge["title"] == "Cuti Banyak!"
        assert nudge["is_read"] is False
        assert "id" in nudge
        assert "created_at" in nudge

    @pytest.mark.asyncio
    async def test_get_unread_nudges(self, service):
        await service.create_nudge(USER_X, "reminder", "Msg 1", "Content 1")
        await service.create_nudge(USER_X, "reminder", "Msg 2", "Content 2")
        nudges = await service.get_user_nudges(USER_X, only_unread=True)
        assert len(nudges) == 2

    @pytest.mark.asyncio
    async def test_get_all_nudges(self, service):
        await service.create_nudge(USER_X, "reminder", "Msg 1", "Content 1")
        nudge = (await service.get_user_nudges(USER_X, only_unread=True))[0]
        await service.mark_as_read(nudge["id"])
        all_nudges = await service.get_user_nudges(USER_X, only_unread=False)
        unread_only = await service.get_user_nudges(USER_X, only_unread=True)
        assert len(all_nudges) == 1
        assert len(unread_only) == 0

    @pytest.mark.asyncio
    async def test_mark_as_read(self, service):
        nudge = await service.create_nudge(USER_X, "reminder", "Test", "Body")
        assert nudge["is_read"] is False
        await service.mark_as_read(nudge["id"])
        nudges = await service.get_user_nudges(USER_X, only_unread=False)
        assert nudges[0]["is_read"] is True

    @pytest.mark.asyncio
    async def test_nudges_isolated_per_user(self, service):
        await service.create_nudge(USER_X, "reminder", "For X", "Content")
        y_nudges = await service.get_user_nudges(USER_Y, only_unread=True)
        assert len(y_nudges) == 0

    @pytest.mark.asyncio
    async def test_nudges_sorted_newest_first(self, service):
        import asyncio
        await service.create_nudge(USER_X, "reminder", "First", "A")
        await asyncio.sleep(0.01)
        await service.create_nudge(USER_X, "reminder", "Second", "B")
        nudges = await service.get_user_nudges(USER_X, only_unread=False)
        assert nudges[0]["title"] == "Second"

    @pytest.mark.asyncio
    async def test_mark_nonexistent_nudge_no_error(self, service):
        # Should not raise an exception
        await service.mark_as_read("nonexistent-id-xyz")

    @pytest.mark.asyncio
    async def test_scan_creates_nudge_for_high_annual_leave(self, service):
        from app.services.data_store import InMemoryStore
        from unittest.mock import patch

        mock_store = InMemoryStore()
        mock_store._leave_balances["test-user"] = {"Annual": 12, "Medical": 14, "Emergency": 5}

        with patch("app.services.nudge_service.NudgeService.scan_for_nudges",
                   wraps=service.scan_for_nudges):
            with patch("app.services.data_store.get_store", return_value=mock_store):
                await service.scan_for_nudges()

        nudges = await service.get_user_nudges("test-user", only_unread=True)
        assert any(n["type"] == "leave_reminder" for n in nudges)

    @pytest.mark.asyncio
    async def test_scan_creates_nudge_for_low_medical_leave(self, service):
        from app.services.data_store import InMemoryStore
        from unittest.mock import patch

        mock_store = InMemoryStore()
        mock_store._leave_balances["sick-user"] = {"Annual": 5, "Medical": 1, "Emergency": 5}

        with patch("app.services.data_store.get_store", return_value=mock_store):
            await service.scan_for_nudges()

        nudges = await service.get_user_nudges("sick-user", only_unread=True)
        assert any(n["type"] == "medical_low" for n in nudges)
