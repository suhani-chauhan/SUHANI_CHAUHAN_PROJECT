from fastapi import Depends

from app.core.security import AuthContext, get_auth_context
from app.db.client import get_user_client
from app.services.task_service import TaskService


def get_task_service(ctx: AuthContext = Depends(get_auth_context)) -> TaskService:
    return TaskService(get_user_client(ctx.token), ctx.user_id)