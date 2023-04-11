from fastapi import FastAPI
import uvicorn

from presentation import (
    schedules_router_v1, schedules_router_v2, status_router
)

fastApi = FastAPI()
fastApi.include_router(schedules_router_v1)
fastApi.include_router(schedules_router_v2)
fastApi.include_router(status_router)

if __name__ == "__main__":
    uvicorn.run(fastApi, host="0.0.0.0", port=80)