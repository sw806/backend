from typing import Any
from fastapi import APIRouter
from application import User, ScheduleTaskRequest

schedules_router = APIRouter(prefix="/api/v1")


@schedules_router.post("/schedules")
async def schedule(request: ScheduleTaskRequest) -> Any:
    try:
        return User().schedule_task(request)
    except Exception as e:
        return "Error: " + str(e)
