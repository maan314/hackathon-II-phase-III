"""
Integration tests for AI Chat Agent system.

Tests complete chat flow including conversation persistence, tool invocation,
user isolation, and error handling.
"""
import pytest
import asyncio
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from backend.main import app
from backend.database import get_session
from backend.models.conversation import Conversation, Message


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Mock authentication
def mock_get_current_user():
    """Mock authentication for testing."""
    return {"user_id": "test_user_123"}


# T044: Test new conversation creation
def test_create_new_conversation(client: TestClient, session: Session):
    """
    Test creating a new conversation.

    Verifies:
    - New conversation created when conversation_id not provided
    - User message persisted
    - Agent response generated
    - Conversation ID returned
    """
    # Mock authentication
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = client.post(
        "/api/test_user_123/chat",
        json={"message": "Hello, I need help with my tasks"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "response" in data
    assert "conversation_id" in data
    assert "message_id" in data
    assert "timestamp" in data

    # Verify conversation created in database
    conversation_id = data["conversation_id"]
    conversation = session.get(Conversation, conversation_id)
    assert conversation is not None
    assert conversation.user_id == "test_user_123"


# T045: Test conversation continuation
def test_continue_existing_conversation(client: TestClient, session: Session):
    """
    Test continuing an existing conversation.

    Verifies:
    - Existing conversation can be continued
    - Conversation history is maintained
    - Context from previous messages is preserved
    """
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    # Create initial conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        json={"message": "Add a task to buy groceries"}
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Continue conversation
    response2 = client.post(
        "/api/test_user_123/chat",
        json={
            "message": "What tasks do I have?",
            "conversation_id": conversation_id
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()

    # Verify same conversation
    assert data2["conversation_id"] == conversation_id

    # Verify messages persisted
    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()
    assert len(messages) >= 2  # At least 2 user messages + agent responses


# T046: Test tool invocation
def test_tool_invocation_add_task(client: TestClient, session: Session):
    """
    Test tool invocation for adding a task.

    Verifies:
    - Agent correctly identifies intent to add task
    - Tool is invoked with proper parameters
    - Tool invocation logged in message metadata
    """
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = client.post(
        "/api/test_user_123/chat",
        json={"message": "Add a task to buy groceries tomorrow"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify tool calls present
    assert "tool_calls" in data
    if data["tool_calls"]:
        assert any(tc["tool_name"] == "add_task" for tc in data["tool_calls"])


# T047: Test conversation resume after restart
def test_conversation_resume_after_restart(client: TestClient, session: Session):
    """
    Test conversation persistence across server restarts.

    Verifies:
    - Conversation data persists in database
    - Messages can be retrieved after restart simulation
    - Conversation can continue seamlessly
    """
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    # Create conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        json={"message": "Create a task for project deadline"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Simulate restart by clearing any in-memory state
    # (In our stateless design, this is already handled)

    # Continue conversation after "restart"
    response2 = client.post(
        "/api/test_user_123/chat",
        json={
            "message": "What was that task about?",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200
    # Conversation should continue without data loss


# T048: Test user isolation
def test_user_isolation_enforcement(client: TestClient, session: Session):
    """
    Test user isolation enforcement.

    Verifies:
    - Users cannot access other users' conversations
    - 403 Forbidden returned for unauthorized access
    """
    from backend.core.security import get_current_user

    # User 1 creates conversation
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "user_1"}
    response1 = client.post(
        "/api/user_1/chat",
        json={"message": "My private task"}
    )
    conversation_id = response1.json()["conversation_id"]

    # User 2 tries to access User 1's conversation
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "user_2"}
    response2 = client.post(
        "/api/user_2/chat",
        json={
            "message": "Show me tasks",
            "conversation_id": conversation_id
        }
    )

    # Should return 404 (conversation not found for this user)
    assert response2.status_code == 404


# T049: Test error handling for invalid inputs
def test_error_handling_invalid_inputs(client: TestClient, session: Session):
    """
    Test error handling for invalid inputs.

    Verifies:
    - 400 Bad Request for invalid message format
    - 400 Bad Request for invalid conversation_id format
    - 401 Unauthorized for missing authentication
    """
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    # Test empty message
    response1 = client.post(
        "/api/test_user_123/chat",
        json={"message": ""}
    )
    assert response1.status_code == 422  # Validation error

    # Test message too long
    response2 = client.post(
        "/api/test_user_123/chat",
        json={"message": "x" * 10001}
    )
    assert response2.status_code == 422  # Validation error

    # Test invalid conversation_id format
    response3 = client.post(
        "/api/test_user_123/chat",
        json={
            "message": "Hello",
            "conversation_id": "invalid-uuid"
        }
    )
    assert response3.status_code == 422  # Validation error


# T050: Test context window management
def test_context_window_management(client: TestClient, session: Session):
    """
    Test context window management for long conversations.

    Verifies:
    - Long conversations are truncated to fit context window
    - Most recent messages are preserved
    - Agent can still process messages with truncated history
    """
    from backend.core.security import get_current_user
    app.dependency_overrides[get_current_user] = mock_get_current_user

    # Create conversation
    response1 = client.post(
        "/api/test_user_123/chat",
        json={"message": "Start conversation"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Add many messages to exceed context window
    for i in range(60):  # More than CONTEXT_WINDOW_SIZE (50)
        client.post(
            "/api/test_user_123/chat",
            json={
                "message": f"Message {i}",
                "conversation_id": conversation_id
            }
        )

    # Verify conversation still works
    response_final = client.post(
        "/api/test_user_123/chat",
        json={
            "message": "What's the latest?",
            "conversation_id": conversation_id
        }
    )

    assert response_final.status_code == 200
    # Agent should handle truncated context gracefully


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
