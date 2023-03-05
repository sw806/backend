from fastapi import APIRouter

from application import User, CheckStatusRequest

status_router = APIRouter(prefix="/api/v1")

@status_router.get("/status")
async def root():
    try:
        user = User()
        request = CheckStatusRequest()
        return user.check_status(request)
    except:
        "Something went wrong."