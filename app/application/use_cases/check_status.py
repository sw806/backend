import os
import psycopg2
from typing import Optional

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class CheckStatusRequest:
    def __init__(self) -> None:
        pass

class CheckStatusResponse:
    def __init__(self, is_healthy: bool, is_connected_to_db: bool, commit_hash: Optional[str] = None) -> None:
        self.is_healthy = is_healthy
        self.is_connected_to_db = is_connected_to_db
        if not commit_hash is None:
            self.commit_hash = commit_hash
        else: self.commit_hash = "Unknown"

class CheckStatusUseCase:
    def __init__(self) -> None:
        pass

    def do(self, _: CheckStatusRequest) -> CheckStatusResponse:
        with tracer.start_as_current_span("CheckDBStatus"):
            connection = psycopg2.connect(
                host="db",
                port=5432,
                user="postgres",
                password="postgres",
                database="price-info"
            )
            could_connect_to_db = connection.closed == 0
            connection.close()
            return CheckStatusResponse(
                True,
                could_connect_to_db,
                os.environ["COMMIT_HASH"]
            )