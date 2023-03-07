from fastapi import APIRouter

from application import User, ScheduleTaskRequest

schedules_router = APIRouter(prefix="/api/v1")

@schedules_router.get("/tasks/{task_id}")
async def root(task_id):
    try:
        user = User()
        request = ScheduleTaskRequest(task_id)
        return user.schedule_task(request)
    except:
        return "Something went wrong!"