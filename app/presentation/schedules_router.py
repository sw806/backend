from typing import Any
from fastapi import APIRouter
from application.use_cases.schedule_tasks import ScheduleTasksRequest
from application import User, ScheduleTaskRequest

schedules_router_v1 = APIRouter(prefix="/api/v1")
schedules_router_v2 = APIRouter(prefix="/api/v2")

@schedules_router_v1.post("/schedules")
async def schedule(request: ScheduleTaskRequest) -> Any:
    try:
        return User().schedule_task(request)
    except Exception as e:
        return "Error: " + str(e)

@schedules_router_v2.post("/schedules")
async def schedule(request: ScheduleTasksRequest) -> Any:
    try:
        print(request)
        return User().schedule_tasks(request)
    except Exception as e:
        return "Error: " + str(e)