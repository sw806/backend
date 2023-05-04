from fastapi import APIRouter

from application import User, CheckStatusRequest

status_router = APIRouter(prefix="/api/v1")

from opentelemetry import trace
tracer = trace.get_tracer(__name__)
@status_router.get("/status")
async def root():
    try:
        with tracer.start_as_current_span("GetStatusRoute"):
            user = User()
            request = CheckStatusRequest()
            return user.check_status(request)
    except:
        "Something went wrong."