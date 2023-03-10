class CheckStatusRequest:
    def __init__(self) -> None:
        pass

class CheckStatusResponse:
    def __init__(self, is_healthy: bool) -> None:
        self.is_healthy = is_healthy
        self.version = "0.1.0"

class CheckStatusUseCase:
    def __init__(self) -> None:
        pass

    def do(self, _: CheckStatusRequest) -> CheckStatusResponse:
        return CheckStatusResponse(True)