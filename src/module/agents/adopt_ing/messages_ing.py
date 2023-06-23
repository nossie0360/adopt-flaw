from __future__ import annotations
import dataclasses
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...util.assignment_with_timestamp import AssignmentWithTimestamp
    from .cost_assessment import CostAssessment
    from .valued_nogood import ValuedNogood
    from ..i_agent import IAgent

from ...util.abstract_messages import Message

@dataclasses.dataclass
class Ok(Message):
    asg: AssignmentWithTimestamp
    tvn: ValuedNogood               # threshold valued nogood
    terminate: bool                 # add for VNE

@dataclasses.dataclass
class AddLink(Message):
    asg: AssignmentWithTimestamp

@dataclasses.dataclass
class Nogood(Message):
    rvn: ValuedNogood               # received valued nogood
    xi: int
    induced_links: list[int]        # list of xi