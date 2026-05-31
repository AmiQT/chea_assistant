"""
Tests for Chin Hin Employee AI Assistant API.

NOTE: App runs with DEV_MODE=true — auth is bypassed, all requests use
the built-in dev admin user (id: 11111111-1111-1111-1111-111111111111).
"""

from unittest.mock import patch, MagicMock


# ================================================
# PUBLIC ENDPOINTS
# ================================================

class TestPublicEndpoints:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "version" in data

    def test_health_has_request_id(self, client):
        response = client.get("/health")
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) == 8

    def test_health_has_response_time(self, client):
        response = client.get("/health")
        assert "x-response-time" in response.headers
        assert "ms" in response.headers["x-response-time"]


# ================================================
# AUTH ENDPOINTS
# ================================================

class TestAuthEndpoints:
    def test_login_valid_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@chinhin.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert "user_id" in data

    def test_login_wrong_password(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@chinhin.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_unknown_user(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@chinhin.com",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_signup_new_user(self, client):
        response = client.post("/api/v1/auth/signup", json={
            "email": "brandnew@chinhin.com",
            "password": "newpass123",
            "full_name": "Brand New User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data

    def test_signup_duplicate_email(self, client):
        response = client.post("/api/v1/auth/signup", json={
            "email": "test@chinhin.com",
            "password": "newpass123"
        })
        assert response.status_code == 400

    def test_login_all_mock_users(self, client):
        users = [
            ("test@chinhin.com", "password123"),
            ("admin@chinhin.com", "admin123"),
            ("hr@chinhin.com", "hr123"),
        ]
        for email, password in users:
            response = client.post("/api/v1/auth/login", json={
                "email": email, "password": password
            })
            assert response.status_code == 200, f"Login failed for {email}"


# ================================================
# AUTH - DEV_MODE behaviour
# (DEV_MODE=true bypasses token check, uses dev admin user)
# ================================================

class TestDevModeAuth:
    def test_users_accessible_in_dev_mode(self, client):
        """DEV_MODE=true: admin dev user returned, so /users is accessible."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_leave_balance_accessible_in_dev_mode(self, client):
        """DEV_MODE=true: leave balance returns 200 with balance data."""
        response = client.get("/api/v1/leaves/balance")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_claims_accessible_in_dev_mode(self, client):
        """DEV_MODE=true: claims list returns 200."""
        response = client.get("/api/v1/claims")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ================================================
# ERROR HANDLING
# ================================================

class TestErrorHandling:
    def test_404_returns_standard_error(self, client):
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert not data["success"]
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "request_id" in data

    def test_method_not_allowed(self, client):
        response = client.patch("/health")
        assert response.status_code == 405
        data = response.json()
        assert not data["success"]
        assert data["error"]["code"] == "METHOD_NOT_ALLOWED"

    def test_validation_error_format(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
        data = response.json()
        assert not data["success"]
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]


# ================================================
# LEAVE ENDPOINTS
# ================================================

class TestLeaveEndpoints:
    def test_leave_types_returns_list(self, client):
        response = client.get("/api/v1/leaves/types")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        types = data["data"]
        assert len(types) == 3
        names = [t["name"] for t in types]
        assert "Annual" in names
        assert "Medical" in names
        assert "Emergency" in names

    def test_leave_balance_returns_all_types(self, client):
        response = client.get("/api/v1/leaves/balance")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        balances = data["data"]
        assert len(balances) == 3
        for b in balances:
            assert "leave_type_name" in b
            assert "remaining_days" in b
            assert "total_days" in b

    def test_apply_leave_success(self, client):
        response = client.post("/api/v1/leaves", json={
            "leave_type": "Annual",
            "start_date": "2026-08-01",
            "end_date": "2026-08-03",
            "reason": "Family trip"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["leave_type"] == "Annual"
        assert data["data"]["days"] == 3

    def test_apply_leave_end_before_start(self, client):
        response = client.post("/api/v1/leaves", json={
            "leave_type": "Annual",
            "start_date": "2026-08-10",
            "end_date": "2026-08-05",
            "reason": "Wrong dates"
        })
        assert response.status_code == 400

    def test_apply_leave_insufficient_balance(self, client):
        """Emergency leave only has 5 days."""
        response = client.post("/api/v1/leaves", json={
            "leave_type": "Emergency",
            "start_date": "2026-09-01",
            "end_date": "2026-09-15",
            "reason": "Way too long emergency"
        })
        assert response.status_code == 400

    def test_get_leave_requests(self, client):
        response = client.get("/api/v1/leaves")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_apply_single_day_leave(self, client):
        """Same start and end date = 1 day."""
        response = client.post("/api/v1/leaves", json={
            "leave_type": "Medical",
            "start_date": "2026-07-15",
            "end_date": "2026-07-15",
            "reason": "Doctor visit"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["days"] == 1


# ================================================
# ROOM ENDPOINTS
# ================================================

class TestRoomEndpoints:
    def test_get_rooms_returns_list(self, client):
        response = client.get("/api/v1/rooms")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        rooms = data["data"]
        assert len(rooms) > 0
        for room in rooms:
            assert "name" in room
            assert "capacity" in room
            assert "is_active" in room

    def test_book_room_success(self, client):
        response = client.post("/api/v1/rooms/bookings", json={
            "room_name": "Bilik Helang",
            "date": "2026-09-15",
            "start_time": "10:00",
            "end_time": "11:00",
            "purpose": "Team sync"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["room_name"] == "Bilik Helang"

    def test_book_room_conflict(self, client):
        """Book same room twice at same time - second should fail."""
        payload = {
            "room_name": "Bilik Merbok",
            "date": "2026-09-20",
            "start_time": "14:00",
            "end_time": "15:00",
            "purpose": "Meeting"
        }
        first = client.post("/api/v1/rooms/bookings", json=payload)
        assert first.status_code == 200

        second = client.post("/api/v1/rooms/bookings", json=payload)
        assert second.status_code == 409

    def test_book_room_missing_fields(self, client):
        response = client.post("/api/v1/rooms/bookings", json={
            "room_name": "Bilik Helang"
        })
        assert response.status_code == 422

    def test_get_all_bookings(self, client):
        response = client.get("/api/v1/rooms/bookings/all")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_cancel_booking(self, client):
        """Book a room then cancel it."""
        book_resp = client.post("/api/v1/rooms/bookings", json={
            "room_name": "Bilik Kelinci",
            "date": "2026-10-01",
            "start_time": "09:00",
            "end_time": "10:00",
            "purpose": "Quick meeting"
        })
        assert book_resp.status_code == 200
        booking_id = book_resp.json()["data"]["id"]

        cancel_resp = client.delete(f"/api/v1/rooms/bookings/{booking_id}")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["success"] is True


# ================================================
# CLAIMS ENDPOINTS
# ================================================

class TestClaimsEndpoints:
    def test_claim_categories_returns_list(self, client):
        response = client.get("/api/v1/claims/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        cats = data["data"]
        assert len(cats) > 0
        for cat in cats:
            assert "id" in cat
            assert "name" in cat
            assert "max_amount" in cat

    def test_submit_claim_success(self, client):
        response = client.post("/api/v1/claims", json={
            "category_id": "cat-1",
            "amount": 35.00,
            "description": "Team lunch"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 35.00
        assert data["data"]["status"] == "pending"

    def test_submit_claim_exceeds_max(self, client):
        """Meal category max is RM50."""
        response = client.post("/api/v1/claims", json={
            "category_id": "cat-1",
            "amount": 200.00,
            "description": "Way too expensive meal"
        })
        assert response.status_code == 400

    def test_submit_claim_invalid_category(self, client):
        response = client.post("/api/v1/claims", json={
            "category_id": "cat-999",
            "amount": 50.00,
            "description": "Invalid category"
        })
        assert response.status_code == 400

    def test_submit_claim_zero_amount(self, client):
        response = client.post("/api/v1/claims", json={
            "category_id": "cat-1",
            "amount": 0.00,
            "description": "Zero amount"
        })
        assert response.status_code == 400

    def test_get_claims_list(self, client):
        response = client.get("/api/v1/claims")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total" in data


# ================================================
# USERS ENDPOINTS
# ================================================

class TestUsersEndpoints:
    def test_get_all_users(self, client):
        """DEV_MODE=true with admin role returns all users."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    def test_get_user_by_id(self, client):
        response = client.get("/api/v1/users/11111111-1111-1111-1111-111111111111")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "11111111-1111-1111-1111-111111111111"

    def test_get_nonexistent_user(self, client):
        response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_user_leaves(self, client):
        response = client.get("/api/v1/users/11111111-1111-1111-1111-111111111111/leaves")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_get_user_claims(self, client):
        response = client.get("/api/v1/users/11111111-1111-1111-1111-111111111111/claims")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ================================================
# NUDGES ENDPOINTS
# ================================================

class TestNudgesEndpoints:
    def test_get_nudges(self, client):
        response = client.get("/api/v1/nudges")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_mark_nudge_read_nonexistent(self, client):
        response = client.post("/api/v1/nudges/nonexistent-id/read")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ================================================
# CHAT ENDPOINT (mocked Azure OpenAI)
# ================================================

class TestChatEndpoint:
    def test_chat_returns_response(self, client):
        """Chat should handle Azure errors gracefully and return 200."""
        response = client.post("/api/v1/chat", json={
            "message": "Hello",
            "user_id": "11111111-1111-1111-1111-111111111111"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data

    def test_chat_with_mocked_azure(self, client):
        """Mock Azure so chat returns proper AI response."""
        mock_message = MagicMock()
        mock_message.content = "Hai! Aku CHEA, boleh bantu kau! 🤖"
        mock_message.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.agents.function_agent.ChatAgentManager.client") as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            response = client.post("/api/v1/chat", json={
                "message": "Berapa cuti aku ada?",
                "user_id": "11111111-1111-1111-1111-111111111111"
            })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    def test_chat_test_endpoint(self, client):
        response = client.get("/api/v1/chat/test")
        assert response.status_code == 200

    def test_chat_conversations_list(self, client):
        response = client.get("/api/v1/chat/conversations")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


# ================================================
# LIVE VISION
# ================================================

class TestLiveVision:
    def test_live_vision_disabled(self, client):
        response = client.get("/api/v1/live/live-vision/token")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "disabled" in data["status"]
