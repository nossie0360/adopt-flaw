from __future__ import annotations
import dataclasses
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...util.assignment_with_timestamp import AssignmentWithTimestamp

from ...util.abstract_messages import AbstractValue, AbstractCost, AbstractThreshold, AbstractTerminate

@dataclasses.dataclass
class RealTree():
    mark: bool
    chain_tree: int

@dataclasses.dataclass
class Value(AbstractValue):
    asg: AssignmentWithTimestamp
    th: int

@dataclasses.dataclass
class Cost(AbstractCost):
    xi: int         # variable id
    context: list[AssignmentWithTimestamp]
    lb: int
    ub: int

@dataclasses.dataclass
class Terminate(AbstractTerminate):
    pass