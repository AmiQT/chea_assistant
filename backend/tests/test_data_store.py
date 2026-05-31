"""
Unit tests for InMemoryStore — pure business logic, no HTTP layer.
"""

import pytest
from app.services.data_store import InMemoryStore


@pytest.fixture
def store():
    """Fresh store per test."""
    return InMemoryStore()


USER_A = "aaaa-aaaa-aaaa-aaaa"
USER_B = "bbbb-bbbb-bbbb-bbbb"


# ================================================
# LEAVE BALANCE
# ================================================

class TestLeaveBalance:
    def test_new_user_gets_default_balance(self, store):
        bal = store.get_leave_balances(USER_A)
        assert bal["Annual"] == 14
        assert bal["Medical"] == 14
        assert bal["Emergency"] == 5

    def test_get_specific_leave_type(self, store):
        assert store.get_leave_balance(USER_A, "Annual") == 14
        assert store.get_leave_balance(USER_A, "Medical") == 14
        assert store.get_leave_balance(USER_A, "Emergency") == 5

    def test_unknown_leave_type_returns_zero(self, store):
        assert store.get_leave_balance(USER_A, "Paternity") == 0

    def test_deduct_leave(self, store):
        new_bal = store.deduct_leave(USER_A, "Annual", 3)
        assert new_bal == 11
        assert store.get_leave_balance(USER_A, "Annual") == 11

    def test_deduct_does_not_go_below_zero(self, store):
        store.deduct_leave(USER_A, "Emergency", 10)  # Only 5 days
        assert store.get_leave_balance(USER_A, "Emergency") == 0

    def test_multiple_deductions(self, store):
        store.deduct_leave(USER_A, "Annual", 5)
        store.deduct_leave(USER_A, "Annual", 3)
        assert store.get_leave_balance(USER_A, "Annual") == 6

    def test_balances_isolated_per_user(self, store):
        store.deduct_leave(USER_A, "Annual", 5)
        assert store.get_leave_balance(USER_B, "Annual") == 14  # User B untouched


# ================================================
# LEAVE APPLICATIONS
# ================================================

class TestLeaveApplications:
    def test_add_leave_application(self, store):
        record = store.add_leave_application(
            USER_A, "Annual", "2026-08-01", "2026-08-03", "Holiday", 3
        )
        assert record["user_id"] == USER_A
        assert record["leave_type"] == "Annual"
        assert record["days"] == 3
        assert record["status"] == "approved"
        assert "id" in record
        assert "created_at" in record

    def test_get_leave_applications_for_user(self, store):
        store.add_leave_application(USER_A, "Annual", "2026-08-01", "2026-08-03", "", 3)
        store.add_leave_application(USER_A, "Medical", "2026-09-01", "2026-09-01", "", 1)
        store.add_leave_application(USER_B, "Annual", "2026-08-05", "2026-08-06", "", 2)

        user_a_leaves = store.get_leave_applications(USER_A)
        assert len(user_a_leaves) == 2

        user_b_leaves = store.get_leave_applications(USER_B)
        assert len(user_b_leaves) == 1

    def test_filter_by_status(self, store):
        store.add_leave_application(USER_A, "Annual", "2026-08-01", "2026-08-03", "", 3)
        approved = store.get_leave_applications(USER_A, status="approved")
        pending = store.get_leave_applications(USER_A, status="pending")
        assert len(approved) == 1
        assert len(pending) == 0

    def test_update_leave_status_to_rejected(self, store):
        record = store.add_leave_application(
            USER_A, "Annual", "2026-08-01", "2026-08-05", "", 5
        )
        store.deduct_leave(USER_A, "Annual", 5)
        bal_before = store.get_leave_balance(USER_A, "Annual")  # 14 - 5 = 9

        store.update_leave_application(record["id"], "rejected", "hr-user")
        bal_after = store.get_leave_balance(USER_A, "Annual")   # Restored to 14

        assert bal_after == bal_before + 5

    def test_get_all_leave_applications(self, store):
        store.add_leave_application(USER_A, "Annual", "2026-08-01", "2026-08-03", "", 3)
        store.add_leave_application(USER_B, "Medical", "2026-09-01", "2026-09-01", "", 1)
        all_apps = store.get_all_leave_applications()
        assert len(all_apps) >= 2


# ================================================
# ROOM BOOKINGS
# ================================================

class TestRoomBookings:
    def test_room_available_by_default(self, store):
        available = store.is_room_available(
            "Bilik Helang", "2026-09-01", "09:00", "10:00"
        )
        assert available is True

    def test_room_not_available_after_booking(self, store):
        store.add_room_booking(USER_A, "Bilik Helang", "2026-09-01", "09:00", "10:00", "Meeting")
        available = store.is_room_available("Bilik Helang", "2026-09-01", "09:00", "10:00")
        assert available is False

    def test_overlapping_slots_blocked(self, store):
        store.add_room_booking(USER_A, "Bilik Merbok", "2026-09-05", "10:00", "12:00", "Training")
        # Partial overlap — start before, end during
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "09:00", "11:00") is False
        # Partial overlap — start during, end after
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "11:00", "13:00") is False
        # Fully inside
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "10:30", "11:30") is False

    def test_adjacent_slots_allowed(self, store):
        store.add_room_booking(USER_A, "Bilik Merbok", "2026-09-05", "10:00", "11:00", "Meeting 1")
        # Starts exactly when previous ends
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "11:00", "12:00") is True
        # Ends exactly when next starts
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "09:00", "10:00") is True

    def test_different_rooms_dont_conflict(self, store):
        store.add_room_booking(USER_A, "Bilik Helang", "2026-09-05", "10:00", "12:00", "Meeting")
        # Different room, same time — should be available
        assert store.is_room_available("Bilik Merbok", "2026-09-05", "10:00", "12:00") is True

    def test_different_dates_dont_conflict(self, store):
        store.add_room_booking(USER_A, "Bilik Helang", "2026-09-05", "10:00", "12:00", "Meeting")
        assert store.is_room_available("Bilik Helang", "2026-09-06", "10:00", "12:00") is True

    def test_add_booking_returns_record(self, store):
        record = store.add_room_booking(USER_A, "Bilik Kelinci", "2026-10-01", "14:00", "15:00", "Review")
        assert record["room_name"] == "Bilik Kelinci"
        assert record["status"] == "confirmed"
        assert "id" in record

    def test_cancel_booking(self, store):
        record = store.add_room_booking(USER_A, "Bilik Helang", "2026-10-10", "09:00", "10:00", "Standup")
        store.cancel_room_booking(record["id"])
        updated = store.get_room_booking_by_id(record["id"])
        assert updated["status"] == "cancelled"

    def test_get_room_bookings_by_date(self, store):
        store.add_room_booking(USER_A, "Bilik Helang", "2026-10-10", "09:00", "10:00", "AM")
        store.add_room_booking(USER_B, "Bilik Helang", "2026-10-10", "14:00", "15:00", "PM")
        store.add_room_booking(USER_A, "Bilik Helang", "2026-10-11", "09:00", "10:00", "Next day")

        bookings = store.get_room_bookings("Bilik Helang", "2026-10-10")
        assert len(bookings) == 2


# ================================================
# CLAIMS
# ================================================

class TestClaims:
    def test_add_claim(self, store):
        record = store.add_claim(
            user_id=USER_A, category_id="cat-1",
            category_name="Meal", amount=45.50,
            description="Team lunch"
        )
        assert record["amount"] == 45.50
        assert record["status"] == "pending"
        assert record["category_name"] == "Meal"
        assert "id" in record

    def test_get_claims_by_user(self, store):
        store.add_claim(USER_A, "cat-1", "Meal", 30.0)
        store.add_claim(USER_A, "cat-2", "Travel", 100.0)
        store.add_claim(USER_B, "cat-1", "Meal", 20.0)

        a_claims = store.get_claims(USER_A)
        assert len(a_claims) == 2
        b_claims = store.get_claims(USER_B)
        assert len(b_claims) == 1

    def test_filter_claims_by_status(self, store):
        store.add_claim(USER_A, "cat-1", "Meal", 30.0)
        pending = store.get_claims(USER_A, status="pending")
        approved = store.get_claims(USER_A, status="approved")
        assert len(pending) == 1
        assert len(approved) == 0

    def test_update_claim_status(self, store):
        record = store.add_claim(USER_A, "cat-1", "Meal", 30.0)
        updated = store.update_claim_status(record["id"], "approved", "hr-user")
        assert updated["status"] == "approved"
        assert updated["actioned_by"] == "hr-user"

    def test_get_claim_by_id(self, store):
        record = store.add_claim(USER_A, "cat-2", "Travel", 150.0, "Grab to office")
        found = store.get_claim_by_id(record["id"])
        assert found is not None
        assert found["amount"] == 150.0

    def test_get_claim_by_nonexistent_id(self, store):
        assert store.get_claim_by_id("nonexistent-id") is None

    def test_get_all_claims(self, store):
        store.add_claim(USER_A, "cat-1", "Meal", 30.0)
        store.add_claim(USER_B, "cat-2", "Travel", 100.0)
        all_claims = store.get_all_claims()
        assert len(all_claims) >= 2


# ================================================
# TRANSPORT BOOKINGS
# ================================================

class TestTransportBookings:
    def test_add_transport_booking(self, store):
        record = store.add_transport_booking(
            USER_A, "Van", "KL Sentral", "2026-09-10", "08:00", "Client visit"
        )
        assert record["vehicle"] == "Van"
        assert record["destination"] == "KL Sentral"
        assert "id" in record


# ================================================
# PENDING HITL ACTIONS
# ================================================

class TestPendingActions:
    def test_set_and_get_pending(self, store):
        action = {"name": "apply_leave", "args": {"leave_type": "Annual"}}
        store.set_pending(USER_A, action)
        assert store.has_pending(USER_A) is True

    def test_pop_pending(self, store):
        action = {"name": "book_room", "args": {"room_name": "Bilik Helang"}}
        store.set_pending(USER_A, action)
        popped = store.pop_pending(USER_A)
        assert popped["name"] == "book_room"
        assert store.has_pending(USER_A) is False

    def test_has_pending_false_by_default(self, store):
        assert store.has_pending(USER_A) is False

    def test_pending_overwritten(self, store):
        store.set_pending(USER_A, {"name": "apply_leave", "args": {}})
        store.set_pending(USER_A, {"name": "book_room", "args": {}})
        popped = store.pop_pending(USER_A)
        assert popped["name"] == "book_room"

    def test_pop_nonexistent_returns_none(self, store):
        assert store.pop_pending("nonexistent-user") is None

    def test_pending_isolated_per_user(self, store):
        store.set_pending(USER_A, {"name": "apply_leave", "args": {}})
        assert store.has_pending(USER_B) is False


# ================================================
# STATIC DATA
# ================================================

class TestStaticData:
    def test_rooms_exist(self, store):
        assert len(store.rooms) == 4
        names = [r["name"] for r in store.rooms]
        assert "Bilik Helang" in names
        assert "Bilik Merbok" in names

    def test_leave_types_exist(self, store):
        assert len(store.leave_types) == 3

    def test_claim_categories_exist(self, store):
        assert len(store.claim_categories) == 5

    def test_daily_menu_has_all_days(self, store):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            assert day in store.daily_menu

    def test_energy_stats_has_all_months(self, store):
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        for month in months:
            assert month in store.energy_stats

    def test_transport_fleet_exists(self, store):
        assert len(store.transport_fleet) == 3
        types = [v["type"] for v in store.transport_fleet]
        assert "Van" in types
        assert "MPV" in types
        assert "Sedan" in types


# ================================================
# DEMO SEED DATA (for main dev user)
# ================================================

class TestSeedData:
    DEMO_USER = "11111111-1111-1111-1111-111111111111"

    def test_demo_user_has_leave_balance(self, store):
        bal = store.get_leave_balances(self.DEMO_USER)
        assert bal["Annual"] == 11  # 14 - 3 used
        assert bal["Medical"] == 14
        assert bal["Emergency"] == 5

    def test_demo_user_has_leave_history(self, store):
        leaves = store.get_leave_applications(self.DEMO_USER)
        assert len(leaves) == 2

    def test_demo_user_has_claims(self, store):
        claims = store.get_claims(self.DEMO_USER)
        assert len(claims) == 2

    def test_demo_room_booking_exists(self, store):
        bookings = store.get_all_room_bookings(user_id=self.DEMO_USER)
        assert len(bookings) == 1
