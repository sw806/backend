from datetime import datetime, timedelta, timezone
from typing import List
from infrastructure.eds_requests import EdsRequests
from infrastructure.postgres_database import PostgresDatabase
from application.use_cases.use_Case import UseCase
from infrastructure.co2_emission_point import Co2EmissionPoint, CO2EmissionsRepository
from pydantic.dataclasses import dataclass


@dataclass
class GetCarbonEmissionIntensityRequest:
    start_time: datetime
    ascending: bool

    def __init__(self, start_time: datetime, ascending: bool = False):
        self.start_time = start_time
        self.ascending = ascending

@dataclass
class GetCarbonEmissionIntensityResponse:
    emission_points: List[Co2EmissionPoint]
    latest_available_emission: datetime

    def __init__(self, emission_points: List[Co2EmissionPoint], latest_available_emission: datetime) -> None:
        self.emission_points = emission_points
        self.latest_available_emission = latest_available_emission

class GetCarbonEmissionIntensityUseCase(UseCase[GetCarbonEmissionIntensityRequest, GetCarbonEmissionIntensityResponse]):
    def __init__(self, fallback: CO2EmissionsRepository) -> None:
        super().__init__()
        self.fallback = fallback
        self.db = PostgresDatabase()
    
    def do(self, request: GetCarbonEmissionIntensityRequest) -> GetCarbonEmissionIntensityResponse:
        latest_emission_point = self.db.get_latest_emission()
        latest_emission_point_time = None if latest_emission_point is None else latest_emission_point.time + timedelta(minutes=5)
        earliest_emission_point = self.db.get_earliest_emission()
        earliest_emission_point_time = None if earliest_emission_point is None else earliest_emission_point.time

        # Spot prices updates everyday at 13.00 danish time or 11.00 utc.
        latest_available_emission = datetime.utcnow()
        latest_available_emission = latest_available_emission.replace(tzinfo=timezone.utc)
        if latest_available_emission.hour > 11:
            # The spot prices have already been released so the next release is tomorrow.
            latest_available_emission = latest_available_emission.replace(
                day=latest_available_emission.day + 1,
                hour=11, # It is not 23 because we work with utc
                minute=0,
                second=0
            )
        else:
            # The spot prices have NOT been released yet.
            latest_available_emission = latest_available_emission.replace(
                day=latest_available_emission.day,
                hour=22,
                minute=0,
                second=0
            )
        
        print(f'Get emissions with latest {latest_available_emission} for {request.start_time}')
        
        # Case 0: The spot prices we are asking for have not been released yet.
        if request.start_time > latest_available_emission:
            raise Exception("Requesting emissions exceeeding EDS prognosis")

        # Case 1: The requested time is earlier than what we have.
        elif earliest_emission_point_time is not None and request.start_time < earliest_emission_point_time:
            print(f'Requested emissions earlier than stored: {request.start_time} -> {earliest_emission_point_time}')
            emissions = EdsRequests().get_co2_emission_prognosis(request.start_time, earliest_emission_point_time)
            self.db.insert_emissions(emissions)

        # Case 2: The requested time is later than what we have
        elif latest_emission_point_time is not None and request.start_time > latest_emission_point_time:
            print(f'Requested emissions later than stored: {request.start_time} -> {latest_emission_point_time}')
            emissions = EdsRequests().get_co2_emission_prognosis(latest_emission_point_time)
            self.db.insert_emissions(emissions)
        
        # Case 3: We have no price points yet.
        elif latest_emission_point is None and earliest_emission_point is None:
            print(f'Initial emissions EDS request')
            emissions = EdsRequests().get_co2_emission_prognosis(request.start_time)
            self.db.insert_emissions(emissions)

        # Case 4: Latest price point is earlier than avaialble point.
        elif latest_emission_point_time is not None and latest_emission_point_time < latest_available_emission:
            print(f'Latest emission is earlier than avaialble point')
            emissions = EdsRequests().get_co2_emission_prognosis(latest_emission_point_time)
            self.db.insert_emissions(emissions)

        emission_points = self.db.get_emissions(request.start_time, request.ascending)
        print(f'Found {len(emission_points)} emissions after {request.start_time}')
        return GetCarbonEmissionIntensityResponse(emission_points, datetime.utcnow())