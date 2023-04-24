from application.use_cases.get_carbon_emission_intensity import GetCarbonEmissionIntensityUseCase
from application.use_cases.schedule_tasks import ScheduleTasksRequest, ScheduleTasksResponse, ScheduleTasksUseCase
from ..use_cases import (
    ScheduleTaskUseCase, ScheduleTaskRequest, ScheduleTaskResponse,
    CheckStatusUseCase, CheckStatusRequest, CheckStatusResponse,
    GetSpotPricesUseCase, GetSpotPricesRequest, GetSpotPricesResponse,
    GetCarbonEmissionIntensityUseCase, GetCarbonEmissionIntensityRequest, GetCarbonEmissionIntensityResponse
)
from infrastructure import (
    EdsRequests
)

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class User:
    def __init__(self) -> None:
        with tracer.start_as_current_span("InitUser"):
            eds = EdsRequests()
            self._get_elspot_prices = GetSpotPricesUseCase()
            self._get_emissions = GetCarbonEmissionIntensityUseCase(eds)
            self._schedule_task = ScheduleTaskUseCase()
            self._schedule_tasks = ScheduleTasksUseCase(
                self._get_elspot_prices,
                self._get_emissions
            )
            self._check_status = CheckStatusUseCase()

    def schedule_task(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        return self._schedule_task.do(request)
    
    def schedule_tasks(self, request: ScheduleTasksRequest) -> ScheduleTasksResponse:
        return self._schedule_tasks.do(request)

    def check_status(self, request: CheckStatusRequest) -> CheckStatusResponse:
        return self._check_status.do(request)

    def get_elspot_prices(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        return self._get_elspot_prices.do(request)

    def get_emissions(self, request: GetCarbonEmissionIntensityRequest) -> GetCarbonEmissionIntensityResponse:
        return self._get_emissions.do(request)