from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundError
from app.dependencies import get_task_service
from app.main import app


def make_task(**overrides) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    task = {
        "id": str(uuid4()), "company_id": str(uuid4()), "title": "Write report",
        "description": None, "status": "pending", "assigned_to": str(uuid4()),
        "created_by": str(uuid4()), "created_at": now, "updated_at": now,
    }
    task.update(overrides)
    return task


class FakeTaskService:
    def __init__(self) -> None:
        self.tasks: list[dict] = []

    def create_task(self, payload):
        task = make_task(title=payload.title, assigned_to=str(payload.assigned_to))
        self.tasks.append(task)
        return task

    def list_tasks(self, status):
        return [t for t in self.tasks if status is None or t["status"] == status.value]

    def update_status(self, task_id, status):
        for task in self.tasks:
            if task["id"] == str(task_id):
                task["status"] = status.value
                return task
        raise NotFoundError("Task not found")


@pytest.fixture
def service() -> FakeTaskService:
    return FakeTaskService()


@pytest.fixture
def client(service):
    app.dependency_overrides[get_task_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_task_returns_201(client):
    res = client.post("/tasks", json={"title": "Ship it", "assigned_to": str(uuid4())})
    assert res.status_code == 201
    assert res.json()["title"] == "Ship it"


def test_create_task_rejects_empty_title(client):
    res = client.post("/tasks", json={"title": "  ", "assigned_to": str(uuid4())})
    assert res.status_code == 422


def test_create_task_rejects_client_supplied_company_id(client):
    body = {"title": "x", "assigned_to": str(uuid4()), "company_id": str(uuid4())}
    assert client.post("/tasks", json=body).status_code == 422


def test_list_tasks_filters_by_status(client, service):
    service.tasks = [make_task(status="pending"), make_task(status="completed")]
    res = client.get("/tasks", params={"status": "completed"})
    assert res.status_code == 200
    assert [t["status"] for t in res.json()] == ["completed"]


def test_update_unknown_task_returns_404(client):
    res = client.patch(f"/tasks/{uuid4()}", json={"status": "completed"})
    assert res.status_code == 404


def test_update_with_invalid_status_returns_422(client):
    res = client.patch(f"/tasks/{uuid4()}", json={"status": "done-ish"})
    assert res.status_code == 422


def test_missing_token_returns_401():
    app.dependency_overrides.clear()
    assert TestClient(app).get("/tasks").status_code == 401
    