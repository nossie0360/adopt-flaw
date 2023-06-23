import copy
import numpy as np

from .message_queue import MessageQueue
from .original_agent_util import OriginalAgentUtil
from ..i_agent import IAgent
from ...util.assignment_with_timestamp import AssignmentWithTimestamp
from ...util.function import Function
from ...util.abstract_messages import Message, AbstractValue, AbstractCost, AbstractThreshold, AbstractTerminate

class TimestampAgentUtil(OriginalAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool=True):
        super().__init__(xi, di, D, disp)
        self._CurrentContext: list[AssignmentWithTimestamp] = []

    def priorityMerge(self, context: list[AssignmentWithTimestamp],
                      context_target: list[AssignmentWithTimestamp]) -> None:
        """
        The recent assignment in context is added to context_target.
        Args:
            context (list[AssignmentWithTimestamp]): source context (not changed).
            context_target (list[AssignmentWithTimestamp]): added context (be changed).
        """
        copy_context = copy.copy(context)
        copy_context_target = copy.copy(context_target)
        for asg_target in copy_context_target:
            for asg in context:
                if asg_target.xi == asg.xi:
                    if asg_target.ID < asg.ID:
                        context_target.remove(asg_target)
                        context_target.append(asg)
                    copy_context.remove(asg)
        #context_target.extend(copy_context)