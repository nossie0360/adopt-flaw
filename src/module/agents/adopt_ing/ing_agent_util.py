import copy
import numpy as np
from typing import overload, Union

from .empty_vn_ca import EmptyCostAssessment, EmptyValuedNogood
from .cost_assessment import CostAssessment
from .valued_nogood import ValuedNogood
from .messages_ing import AddLink, Nogood, Ok
from ..util.message_queue import MessageQueue
from ..i_agent import IAgent
from ...util.assignment import Assignment
from ...util.assignment_with_timestamp import AssignmentWithTimestamp
from ...util.function import Function
from ...util.abstract_messages import Message

class IngAgentUtil(IAgent):
    def __init__(self, xi: int, di: int, D: int, disp: bool=True):
        self._xi: int = xi      # variable id
        self._di: int = di      # variable value
        self._D: list[int] = D      # domain
        self._fset: list[Function] = []      # cost functions (type: Functions)
        self._parent: IAgent = None
        self._children: list[IAgent] = []
        self._neighbor: list[IAgent] = []
        self._lower_neighbor: list[IAgent] = []     # descendants (include children)
        self._ancestors: list[IAgent] = []
        self._scp: list[IAgent] = []
        self._all_agents: list[IAgent] = []
        self._subtree: dict[int, int] = {}      # _subtree[agent_id] -> subtree_id
        self._depth: int = 0
        self._depth_tree: int = 0
        self._message_queue: MessageQueue = MessageQueue()
        self._clock: int = 0
        self._exec_terminate: bool = False
        self._disp: bool = disp
        self._agent_view: list[AssignmentWithTimestamp] = []

    @property
    def xi(self) -> int:
        return self._xi

    @property
    def di(self) -> int:
        return self._di

    @property
    def D(self) -> list[int]:
        return self._D

    @property
    def fset(self) -> list[Function]:
        return self._fset

    @property
    def parent(self) -> IAgent:
        return self._parent

    @parent.setter
    def parent(self, parent: IAgent):
        self._parent = parent

    @property
    def children(self) -> list[IAgent]:
        return self._children

    @property
    def neighbor(self) -> list[IAgent]:
        return self._neighbor

    @property
    def lower_neighbor(self) -> list[IAgent]:
        return self._lower_neighbor

    @property
    def ancestors(self) -> list["IAgent"]:
        return self._ancestors

    @ancestors.setter
    def ancestors(self, ancestors: list["IAgent"]):
        self._ancestors = ancestors

    @property
    def scp(self) -> list[IAgent]:
        """
        a set of ancestors which share a constrant with the agent or its descendant.
        """
        return self._scp

    @scp.setter
    def scp(self, s: set["IAgent"]):
        self._scp = s

    @property
    def all_agents(self) -> list["IAgent"]:
        return self._all_agents

    @all_agents.setter
    def all_agents(self, all_agents: list["IAgent"]):
        self._all_agents = all_agents


    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, d: int):
        self._depth = d

    @property
    def depth_tree(self) -> int:
        return self._depth_tree

    @depth_tree.setter
    def depth_tree(self, d: int):
        self._depth_tree = d

    @property
    def message_queue(self) -> MessageQueue:
        return self._message_queue

    @message_queue.setter
    def message_queue(self, msg_queue: MessageQueue):
        self._message_queue = msg_queue

    def setClock(self, clock_time: int = None):
        """
        set the clock of the agent.
        If time is not given, increment the current clock.
        """
        if clock_time is None:
            self._clock = self._clock + 1
        else:
            self._clock = clock_time

    def addFuntion(self, f):
        self._fset.append(f)

    def addMessage(self, msg: Message):
        return self._message_queue.addMessage(msg)

    def updateMessageQueue(self):
        return self._message_queue.updateMessageQueue()

    def getMessageQueueLength(self) -> int:
        return self._message_queue.getLength()

    def isTerminated(self):
        return self._exec_terminate

    def getAgent(self, xi: int, agent_list: list[IAgent]) -> IAgent:
        for agent in agent_list:
            if agent.xi == xi:
                return agent

    # get Assignment from a set of assignments
    def getAssignment(self, asg_list: list[Assignment], xi: int):
        for asg in asg_list:
            if asg.xi == xi:
                return asg.di
        return None

    def isNewAssignment(self, asg: AssignmentWithTimestamp,\
                        asg_list: list[AssignmentWithTimestamp]) -> bool:
        if asg.xi not in [asg.xi for asg in asg_list]:
            return True
        for contained_asg in asg_list:
            if contained_asg.xi == asg.xi:
                return contained_asg.ID < asg.ID

    def removeAssignment(self, asg_list: list[Assignment], xi: int) -> list[Assignment]:
        new_asg_list = copy.copy(asg_list)
        for asg in asg_list:
            if asg.xi == xi:
                new_asg_list.remove(asg)
        return new_asg_list

    def addToAgentView(self, new_asg: Assignment):
        for asg in self._agent_view:
            if asg.xi == new_asg.xi:
                self._agent_view.remove(asg)
        self._agent_view.append(new_asg)
        return

    def isCompatible(self, view_one: list[Assignment], view_two: list[Assignment]):
        for asg in view_one:
            for cur_asg in view_two:
                if asg.xi == cur_asg.xi:
                    if asg.di == cur_asg.di: break
                    else: return False
        return True

    @overload
    def isEmpty(self, ca: CostAssessment):
        pass

    @overload
    def isEmpty(self, nogood: ValuedNogood):
        pass

    def isEmpty(self, ca: Union[CostAssessment, ValuedNogood]):
        if isinstance(ca, CostAssessment):
            return isinstance(ca, EmptyCostAssessment)
        if isinstance(ca, ValuedNogood):
            return isinstance(ca, EmptyValuedNogood)

    @overload
    def targetId(self, nogood: ValuedNogood) -> int:
        pass

    @overload
    def targetId(self, ca: CostAssessment) -> int:
        pass

    def targetId(self, ca: Union[ValuedNogood, CostAssessment]) -> int:
        variable_id = [asg.xi for asg in ca.asg_set]
        if len(variable_id) > 0:
            return max(variable_id)
        else:
            return -1

    def getAgentsIdInSameSubtree(self, subtree_id: int) -> list[int]:
        return [xi for xi in self._subtree if self._subtree[xi] == subtree_id]

    def getCost(self, ca: CostAssessment):
        return ca.cost

    def transformToValuedNogood(self, ca: CostAssessment, xi: int, time_stamp: int)\
            -> ValuedNogood:
        if isinstance(ca, EmptyCostAssessment):
            return EmptyValuedNogood()
        src = ca.src
        exact = ca.exact
        cost = ca.cost
        asg_set = ca.asg_set.union(\
            {AssignmentWithTimestamp(xi, ca.value, time_stamp)})
        return ValuedNogood(src, exact, cost, asg_set)

    def transformToCostAssessment(self, nogood: ValuedNogood, xi: int, d: int)\
            -> CostAssessment:
        """
        transform the given valued nogood into the corresponding cost assessment
        (used Remark 3 if needed.)
        If the assignment for xi of nogood is incompatible with given (xi, d),
        it returns an empty one.
        """
        if isinstance(nogood, EmptyValuedNogood):
            return EmptyCostAssessment(d)
        src = nogood.src
        exact = nogood.exact
        cost = nogood.cost
        asg_set = copy.deepcopy(nogood.asg_set)
        di_asg = self.getAssignment(list(asg_set), xi)
        if di_asg is not None:
            asg_set = set(self.removeAssignment(list(asg_set), xi))
            if di_asg != d:
                return EmptyCostAssessment(d)
        return CostAssessment(src, di_asg, exact, cost, asg_set)

    def argminCostAssessment(self, ca_dict: dict[int, CostAssessment]) -> int:
        cost_dict = {key: self.getCost(ca_dict[key]) for key in ca_dict}
        min_key = min(cost_dict, key=cost_dict.get)
        min_cost = min(cost_dict.values())
        if min_cost == cost_dict[self._di]:
            min_key = self._di
        return min_key

    def minCostAssessment(self, ca_dict: dict[int, CostAssessment])\
          -> CostAssessment:
        min_key = self.argminCostAssessment(ca_dict)
        return ca_dict[min_key]

    def getLocalCostAssessment(self, d: int)\
            -> CostAssessment:
        """
        return a local cost assessment using all variables in the agent_view.
        """
        sum_cost: int = 0
        evaluated_functions: dict[int, bool] =\
              {fn.f_id: False for fn in self._fset}
        for asg in self._agent_view:
            xj = asg.xi
            dj = asg.di
            for fn in self._fset:
                if fn.sp.xi == xj:
                    sum_cost = sum_cost + fn.f(dj, d)
                    evaluated_functions[fn.f_id] = True
                    break
                elif fn.ep.xi == xj:
                    sum_cost = sum_cost + fn.f(d, dj)
                    evaluated_functions[fn.f_id] = True
                    break
        references = {key for key in evaluated_functions if evaluated_functions[key]}
        exact = all(evaluated_functions.values())
        if len(references) > 0:
            return CostAssessment(references, d, exact, sum_cost, set(self._agent_view))
        else:
            return EmptyCostAssessment(d)

    def getPartialLocalCostFunctions(self, considered_agents: list[IAgent])\
            -> list[Function]:
        """
        return a set of cost functions involved by only its variables or ones in considered_agents.
        """
        ret_functions = []
        for fn in self._fset:
            if fn.sp == fn.ep\
                or fn.sp in considered_agents or fn.ep in considered_agents:
                ret_functions.append(fn)
        return ret_functions

    def getPartialAgentView(self, agent_view: list[AssignmentWithTimestamp],\
                            considered_agents: list[IAgent]):
        considered_id = [agent.xi for agent in considered_agents]
        return [asg for asg in agent_view if asg.xi in considered_id]

    def getPartialLocalCostAssessment(self, d: int, considered_agents: list[IAgent])\
            -> CostAssessment:
        """
        return a cost assessment using only variables in considered_agents.
        """
        considered_functions = self.getPartialLocalCostFunctions(considered_agents)
        considered_view = self.getPartialAgentView(self._agent_view, considered_agents)
        sum_cost: int = 0
        evaluated_functions: dict[int, bool] =\
              {fn.f_id: False for fn in considered_functions}
        for asg in considered_view:
            xj = asg.xi
            dj = asg.di
            for fn in considered_functions:
                if fn.sp.xi == xj:
                    sum_cost = sum_cost + fn.f(dj, d)
                    evaluated_functions[fn.f_id] = True
                    break
                elif fn.ep.xi == xj:
                    sum_cost = sum_cost + fn.f(d, dj)
                    evaluated_functions[fn.f_id] = True
                    break
        references =  {key for key in evaluated_functions if evaluated_functions[key]}
        exact = all(evaluated_functions.values())
        if len(references) > 0:
            return CostAssessment(references, d, exact, sum_cost, set(considered_view))
        else:
            return EmptyCostAssessment(d)

    @overload
    def isComposedOnlyOfConsideredAgents(self, ca: CostAssessment,\
                                        considered_agents: list[IAgent]) -> bool:
        pass

    @overload
    def isComposedOnlyOfConsideredAgents(self, nogood: ValuedNogood,\
                                        considered_agents: list[IAgent]) -> bool:
        pass

    def isComposedOnlyOfConsideredAgents(self, nogood: Union[ValuedNogood, CostAssessment],\
                                        considered_agents: list[IAgent]) -> bool:
        considered_variables = [agent.xi for agent in considered_agents]
        for asg in nogood.asg_set:
            if asg.xi not in considered_variables:
                return False
        return True

    def getPrefixAgents(self, agents: list[IAgent], end_agent: IAgent)\
            -> list[IAgent]:
        """
        return a prefix of the sorted agent list to end_agent.
        The sort is used agents' id, or xi.

        Example:
            getPrefixAgents([Agent(xi=1), Agent(xi=0), Agent(xi=3)], Agent(xi=1))

            -> [Agent(xi=0), Agent(xi=1)]
        """
        sorted_list = sorted(agents, key=lambda agent: agent.xi)
        for i, agent in enumerate(sorted_list):
            if agent == end_agent:
                end_agent_idx = i
                break
        return sorted_list[0:end_agent_idx + 1]

    def backTrack(self):
        pass

    def processMessage(self):
        if self.message_queue.isEmpty() or self.isTerminated():
            return False
        msg = self.message_queue.pop(0)
        self.receive(msg)
        #if self.message_queue.isEmpty():
        #    self.backTrack()
        return True

    def send(self, msg: Message, dst_agent: IAgent):
        if dst_agent is None: return

        # <DISP>
        if self._disp:
            mtype = ""
            if isinstance(msg, AddLink):
                mtype = "add-link"
            elif isinstance(msg, Nogood):
                mtype = "nogood"
            elif isinstance(msg, Ok):
                mtype = "ok?"
            print("[{}] {} -> {} : ".format(mtype, self._xi, dst_agent.xi), msg)
        # </DISP>

        msg.from_xi = self._xi
        msg.sent_clock = self._clock
        dst_agent.addMessage(copy.deepcopy(msg))