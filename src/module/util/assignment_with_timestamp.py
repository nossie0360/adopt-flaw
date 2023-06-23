import dataclasses
from .assignment import Assignment

@dataclasses.dataclass(frozen=True)
class AssignmentWithTimestamp(Assignment):
    ID: int     # timestamp