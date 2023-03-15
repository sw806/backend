from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar


TDomain = TypeVar("TDomain")
TCodomain = TypeVar("TCodomain")
TIntegral = TypeVar("TIntegral")

class Function(ABC, Generic[TDomain, TCodomain, TIntegral]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def apply(self, argument: TDomain) -> TCodomain:
        """Apply a value (the argument) form its domain to obtain the the corresponding value from its range.

        Args:
            argument (TDomain): The argument from the domain.

        Returns:
            TCodomain: The range value from the codomain.
        """
        pass

    @abstractmethod
    def integrate(self, start: TDomain, end: TDomain) -> TIntegral:
        """Calculates the area between (inclusive) the start and end arguments.

        Args:
            start (TDomain): The start argument from the domain.
            end (TDomain): The end argument from the domain.

        Returns:
            TIntegral: The area under the funciton from start to end.
        """
        pass