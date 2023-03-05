from ..use_cases import (
    ScheduleTaskUseCase, ScheduleTaskRequest, ScheduleTaskResponse,
    CheckStatusUseCase, CheckStatusRequest, CheckStatusResponse
)

class User:
    def __init__(self) -> None:
        self._schedule_task = ScheduleTaskUseCase()
        self._check_status = CheckStatusUseCase()

    def schedule_task(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        return self._schedule_task.do(request)
    
    def check_status(self, request: CheckStatusRequest) -> CheckStatusResponse:
        return self._check_status.do(request)