from __future__ import annotations
import dataclasses
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...util.assignment import Assignment

from ...util.abstract_messages import AbstractValue, AbstractCost, AbstractThreshold, AbstractTerminate

@dataclasses.dataclass
class Value(AbstractValue):
    asg: Assignment

@dataclasses.dataclass
class Cost(AbstractCost):
    xi: int         # variable id
    context: list[Assignment]
    lb: int
    ub: int

@dataclasses.dataclass
class Threshold(AbstractThreshold):
    t: int        # threshold
    context: list[Assignment]

@dataclasses.dataclass
class Terminate(AbstractTerminate):
    t: int      # threshold
    context: list[Assignment]