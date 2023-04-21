from application.use_cases.get_spot_price_task import GetSpotPricesUseCase
from application.use_cases.get_carbon_emission_intensity import GetCarbonEmissionIntensityUseCase
from application.use_cases.schedule_tasks import ScheduleTasksRequest, ScheduleTasksResponse, ScheduleTasksUseCase
from ..use_cases import (
    ScheduleTaskUseCase, ScheduleTaskRequest, ScheduleTaskResponse,
    CheckStatusUseCase, CheckStatusRequest, CheckStatusResponse
)
from infrastructure import (
    EdsRequests
)

class User:
    def __init__(self) -> None:
        eds = EdsRequests()
        self._schedule_task = ScheduleTaskUseCase()
        self._schedule_tasks = ScheduleTasksUseCase(
            GetSpotPricesUseCase(),
            GetCarbonEmissionIntensityUseCase(eds)
        )
        self._check_status = CheckStatusUseCase()

    def schedule_task(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        return self._schedule_task.do(request)
    
    def schedule_tasks(self, request: ScheduleTasksRequest) -> ScheduleTasksResponse:
        return self._schedule_tasks.do(request)

    def check_status(self, request: CheckStatusRequest) -> CheckStatusResponse:
        return self._check_status.do(request)