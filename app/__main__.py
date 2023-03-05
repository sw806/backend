from fastapi import FastAPI
import uvicorn

from presentation import (
    tasks_router, status_router
)

fastApi = FastAPI()
fastApi.include_router(tasks_router)
fastApi.include_router(status_router)

if __name__ == "__main__":
    uvicorn.run(fastApi, host="0.0.0.0", port=8000)