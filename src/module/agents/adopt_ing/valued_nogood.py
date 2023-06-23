import dataclasses

from ...util.assignment_with_timestamp import AssignmentWithTimestamp

@dataclasses.dataclass
class ValuedNogood():
    src: set[int]       # a Set of References to Constraints
    exact: bool
    cost: int
    asg_set: set[AssignmentWithTimestamp]
