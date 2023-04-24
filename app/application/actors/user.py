from application.use_cases.get_spot_price_task import GetSpotPricesUseCase
from application.use_cases.schedule_tasks import ScheduleTasksRequest, ScheduleTasksResponse, ScheduleTasksUseCase
from ..use_cases import (
    ScheduleTaskUseCase, ScheduleTaskRequest, ScheduleTaskResponse,
    CheckStatusUseCase, CheckStatusRequest, CheckStatusResponse
)

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class User:
    def __init__(self) -> None:
        with tracer.start_as_current_span("InitUser"):
            self._schedule_task = ScheduleTaskUseCase()
            self._schedule_tasks = ScheduleTasksUseCase(
                GetSpotPricesUseCase()
            )
            self._check_status = CheckStatusUseCase()

    def schedule_task(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        return self._schedule_task.do(request)
    
    def schedule_tasks(self, request: ScheduleTasksRequest) -> ScheduleTasksResponse:
        return self._schedule_tasks.do(request)

    def check_status(self, request: CheckStatusRequest) -> CheckStatusResponse:
        return self._check_status.do(request)