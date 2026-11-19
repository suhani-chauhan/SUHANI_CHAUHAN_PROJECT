from uuid import UUID

from supabase import Client

from app.core.exceptions import ForbiddenError, NotFoundError, UnprocessableError
from app.schemas.task import TaskCreate, TaskStatus


class TaskService:
    def __init__(self, client: Client, user_id: UUID) -> None:
        self._client = client
        self._user_id = user_id

    def _get_profile(self) -> dict:
        res = (
            self._client.table("users")
            .select("id, company_id, role")
            .eq("id", str(self._user_id))
            .limit(1)
            .execute()
        )
        if not res.data:
            raise ForbiddenError("User profile not found")
        return res.data[0]

    def create_task(self, payload: TaskCreate) -> dict:
        profile = self._get_profile()
        if profile["role"] != "manager":
            raise ForbiddenError("Only managers can create tasks")

        assignee = (
            self._client.table("users")
            .select("id")
            .eq("id", str(payload.assigned_to))
            .eq("company_id", profile["company_id"])
            .limit(1)
            .execute()
        )
        if not assignee.data:
            raise UnprocessableError("Assignee does not exist in your company")

        row = {
            "company_id": profile["company_id"],  # derived server-side, never from client
            "title": payload.title,
            "description": payload.description,
            "assigned_to": str(payload.assigned_to),
            "created_by": str(self._user_id),
        }
        return self._client.table("tasks").insert(row).execute().data[0]

    def list_tasks(self, status: TaskStatus | None = None) -> list[dict]:
        profile = self._get_profile()
        query = (
            self._client.table("tasks")
            .select("*")
            .eq("company_id", profile["company_id"])
            .order("created_at", desc=True)
        )
        if status is not None:
            query = query.eq("status", status.value)
        return query.execute().data

    def update_status(self, task_id: UUID, status: TaskStatus) -> dict:
        profile = self._get_profile()
        res = (
            self._client.table("tasks")
            .update({"status": status.value})
            .eq("id", str(task_id))
            .eq("company_id", profile["company_id"])
            .execute()
        )
        if not res.data:
            # Same response whether the task doesn't exist or belongs to someone else
            raise NotFoundError("Task not found")
        return res.data[0]