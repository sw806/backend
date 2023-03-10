import os
from typing import Optional

class CheckStatusRequest:
    def __init__(self) -> None:
        pass

class CheckStatusResponse:
    def __init__(self, is_healthy: bool, commit_hash: Optional[str] = None) -> None:
        self.is_healthy = is_healthy
        if not commit_hash is None:
            self.commit_hash = commit_hash
        else: self.commit_hash = "Unknown"

class CheckStatusUseCase:
    def __init__(self) -> None:
        pass

    def do(self, _: CheckStatusRequest) -> CheckStatusResponse:
        return CheckStatusResponse(
            True,
            os.environ["COMMIT_HASH"]
        )