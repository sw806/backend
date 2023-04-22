import traceback
from datetime import datetime, timezone
from fastapi import Response
from fastapi import APIRouter
from application import (
    User,
    GetCarbonEmissionIntensityRequest,
    GetCarbonEmissionIntensityResponse
)

emissions_router_v1 = APIRouter(prefix='/api/v1')

@emissions_router_v1.get("/emissions")
async def get_emissions(response: Response) -> GetCarbonEmissionIntensityResponse | str:
    try:
        now = datetime.utcnow()
        now = now.replace(tzinfo=timezone.utc)
        request = GetCarbonEmissionIntensityRequest(now)
        return User().get_emissions(request)
    except Exception as e:
        print(traceback.format_exc())
        response.status_code = 500
        return "Error: " + str(e)