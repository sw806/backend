from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

class UseCase(ABC, Generic[TRequest, TResponse]):
    @abstractmethod
    def do(self, request: TRequest) -> TResponse:
        pass