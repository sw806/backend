import traceback
from datetime import datetime, timezone
from fastapi import Response
from fastapi import APIRouter
from application import (
    User,
    GetSpotPricesRequest,
    GetSpotPricesResponse
)

spot_prices_router_v1 = APIRouter(prefix='/api/v1')

@spot_prices_router_v1.get("/spot_prices")
async def get_elspot_prices(response: Response) -> GetSpotPricesResponse | str:
    try:
        now = datetime.utcnow()
        now = now.replace(tzinfo=timezone.utc)
        request = GetSpotPricesRequest(now)
        return User().get_elspot_prices(request)
    except Exception as e:
        print(traceback.format_exc())
        response.status_code = 500
        return "Error: " + str(e)