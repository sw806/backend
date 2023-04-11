from typing import List
from .task_validator_conjunction import TaskValidatorConjunction
from .task_validator_disjunction import TaskValidatorDisjunction
from .must_start_between_validator import MustStartBetweenValidator
from .must_end_between_validator import MustEndBetweenValidator
from .task_validator_visitor import TaskValidatorVisitor

class TaskValidatorSplit:
    must_start_between_validators: List[MustStartBetweenValidator]
    must_end_between_validators: List[MustEndBetweenValidator]

class TaskValidatorSplitter(TaskValidatorVisitor[None]):
    split: TaskValidatorSplit

    def visit_conjunction(self, conjunction: TaskValidatorConjunction) -> None:
        for validator in conjunction.validators:
            return self.visit(validator)

    def visit_disjunction(self, disjunction: TaskValidatorDisjunction) -> None:
        for validator in disjunction.validators:
            return self.visit(validator)

    def visit_must_start_between(self, validator: MustStartBetweenValidator) -> None:
        self.split.must_start_between_validators.append(validator)

    def visit_must_end_between(self, validator: MustEndBetweenValidator) -> None:
        self.split.must_end_between_validators.append(validator)
