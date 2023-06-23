import dataclasses

from ...util.assignment_with_timestamp import AssignmentWithTimestamp

@dataclasses.dataclass
class CostAssessment():
    src: set[int]       # a Set of References to Constraints
    value: int
    exact: bool
    cost: int
    asg_set: set[AssignmentWithTimestamp]