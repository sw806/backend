from fastapi import APIRouter
from app.application import User, ScheduleTaskRequest

schedules_router = APIRouter(prefix="/api/v1")


@schedules_router.post("/schedules")
async def schedule(request: ScheduleTaskRequest):
    try:
        return User().schedule_task(request)
    except:
        return "Something went wrong!"