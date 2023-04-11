from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from .task import TaskValidator
from .task_validator_conjunction import TaskValidatorConjunction
from .task_validator_disjunction import TaskValidatorDisjunction
from .must_start_between_validator import MustStartBetweenValidator
from .must_end_between_validator import MustEndBetweenValidator

TVisitor = TypeVar("TVisitor")

class TaskValidatorVisitor(ABC, Generic[TVisitor]):
    def __init__(self) -> None:
        super().__init__()

    def visit(self, validator: TaskValidator) -> TVisitor:
        if isinstance(validator, TaskValidatorConjunction):
            return self.visit_conjunction(validator)
        elif isinstance(validator, TaskValidatorDisjunction):
            return self.visit_disjunction(validator)
        elif isinstance(validator, MustStartBetweenValidator):
            return self.visit_must_start_between(validator)
        elif isinstance(validator, MustEndBetweenValidator):
            return self.visit_must_end_between(validator)
        raise Exception("Unsupported validator")

    @abstractmethod
    def visit_conjunction(self, validator: TaskValidatorConjunction) -> TVisitor:
        pass

    @abstractmethod
    def visit_disjunction(self, validator: TaskValidatorDisjunction) -> TVisitor:
        pass

    @abstractmethod
    def visit_must_start_between(self, validator: MustStartBetweenValidator) -> TVisitor:
        pass

    @abstractmethod
    def visit_must_end_between(self, validator: MustEndBetweenValidator) -> TVisitor:
        pass