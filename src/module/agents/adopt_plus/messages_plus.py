from __future__ import annotations
import dataclasses
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...util.assignment_with_timestamp import AssignmentWithTimestamp

from ...util.abstract_messages import AbstractValue, AbstractCost, AbstractThreshold, AbstractTerminate

@dataclasses.dataclass
class Value(AbstractValue):
    asg: AssignmentWithTimestamp
    t: int      # threshold
    context: list[AssignmentWithTimestamp]


@dataclasses.dataclass
class Cost(AbstractCost):
    xi: int         # variable id
    context: list[AssignmentWithTimestamp]
    lb: int
    ub: int
    th_req: bool

@dataclasses.dataclass
class Terminate(AbstractTerminate):
    context: list[AssignmentWithTimestamp]