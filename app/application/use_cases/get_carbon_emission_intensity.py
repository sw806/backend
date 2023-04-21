from datetime import datetime
from typing import List
from application.use_cases.use_Case import UseCase
from infrastructure.co2_emission_point import Co2EmissionPoint, CO2EmissionsRepository


class GetCarbonEmissionIntensityRequest:
    def __init__(self, start_time: datetime, ascending: bool = False):
        self.start_time = start_time
        self.ascending = ascending

class GetCarbonEmissionIntensityResponse:
    def __init__(self, emission_points: List[Co2EmissionPoint]) -> None:
        self.emission_points = emission_points

class GetCarbonEmissionIntensityUseCase(UseCase[GetCarbonEmissionIntensityRequest, GetCarbonEmissionIntensityResponse]):
    def __init__(self, repository: CO2EmissionsRepository) -> None:
        super().__init__()
        self.repository = repository
    
    def do(self, request: GetCarbonEmissionIntensityRequest) -> GetCarbonEmissionIntensityResponse:
        emission_points = self.repository.get_co2_emission_prognosis(request.start_time)
        return GetCarbonEmissionIntensityResponse(emission_points)