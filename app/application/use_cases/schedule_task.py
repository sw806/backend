class ScheduleTaskRequest:
    def __init__(self, msg: str) -> None:
        self.msg = msg

class ScheduleTaskResponse:
    def __init__(self, msg: str) -> None:
        self.msg = msg

class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        return ScheduleTaskResponse(
            f"Hello! I got '{request.msg}' and I send you this."
        )