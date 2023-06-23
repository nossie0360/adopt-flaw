import dataclasses

from .cost_assessment import CostAssessment
from .valued_nogood import ValuedNogood

class EmptyCostAssessment(CostAssessment):
    def __init__(self, d: int):
        self.src = set()
        self.value = d
        self.exact = False
        self.cost = 0
        self.asg_set = set()

class EmptyValuedNogood(ValuedNogood):
    def __init__(self):
        self.src = set()
        self.exact = False
        self.cost = 0
        self.asg_set = set()