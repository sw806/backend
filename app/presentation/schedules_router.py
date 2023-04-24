import traceback
from typing import Any, Union
from fastapi import Response
from fastapi import APIRouter
from application import (
    User,
    ScheduleTaskRequest,
    ScheduleTaskResponse,
    ScheduleTasksRequest,
    ScheduleTasksResponse
)

schedules_router_v1 = APIRouter(prefix="/api/v1")
schedules_router_v2 = APIRouter(prefix="/api/v2")

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@schedules_router_v1.post("/schedules")
async def schedule_v1(request: ScheduleTaskRequest, response: Response) -> ScheduleTaskResponse | str:
    try:
        with tracer.start_as_current_span("PostSchedulesV1"):
            return User().schedule_task(request)
    except Exception as e:
        print(traceback.format_exc())
        response.status_code = 500
        return "Error: " + str(e)

@schedules_router_v2.post("/schedules")
async def schedule_v2(request: ScheduleTasksRequest, response: Response) -> ScheduleTasksResponse | str:
    try:
        with tracer.start_as_current_span("PostSchedulesV2"):
            scheduler_response = User().schedule_tasks(request)
            if scheduler_response.schedule is None or\
                len(scheduler_response.schedule.tasks) == 0:
                response.status_code = 400
                return ""
            else:
                return User().schedule_tasks(request)
    except Exception as e:
        print(traceback.format_exc())
        response.status_code = 500
        return "Error: " + str(e)