from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from app.dependencies import get_task_service
from app.schemas.task import TaskCreate, TaskOut, TaskStatus, TaskStatusUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=http_status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(payload)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: TaskStatus | None = Query(default=None),
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks(status)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task_status(
    task_id: UUID,
    payload: TaskStatusUpdate,
    service: TaskService = Depends(get_task_service),
):
    return service.update_status(task_id, payload.status)