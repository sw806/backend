from fastapi import FastAPI
import uvicorn

from presentation import (
    schedules_router_v1, schedules_router_v2, status_router,
    spot_prices_router_v1, emissions_router_v1
)

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())

fastApi = FastAPI()
fastApi.include_router(schedules_router_v1)
fastApi.include_router(schedules_router_v2)
fastApi.include_router(status_router)
fastApi.include_router(spot_prices_router_v1)
fastApi.include_router(emissions_router_v1)

if __name__ == "__main__":
    uvicorn.run(fastApi, host="0.0.0.0", port=80)
