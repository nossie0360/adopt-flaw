import copy
import numpy as np

from ..util.timestamp_agent_util import TimestampAgentUtil
from ..i_agent import IAgent
from ...util.abstract_messages import Message
from .messages_k import Value, Cost, Terminate
from ...util.assignment_with_timestamp import AssignmentWithTimestamp

class KAgent(TimestampAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    # ADOPT implement
    def initialize(self):
        self._exec_terminate: bool = False
        self._terminate: bool = False
        self._k = 1
        self._threshold_a: float = 0
        self._threshold_d: dict[int, float] = {}
        self._threshold_b: float = 0
        self._CurrentContext: list[AssignmentWithTimestamp] = \
            [AssignmentWithTimestamp(na.xi, 0, 0) for na in self._scp]
        self._ID: int = 0
        self._lb: dict[int, dict[int, float]] = {}
        self._ub: dict[int, dict[int, float]] = {}
        self._th: dict[int, dict[int, float]] = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}; self._th[d] = {}; self._threshold_d[d] = 0
            for child in self._children:
                self.initChild(d, child)
        self.initSelf()
        self.backTrack()

    def initChild(self, d: int, child: IAgent):
        xl = child.xi
        self._lb[d][xl] = 0
        self._ub[d][xl] = np.inf
        self._th[d][xl] = self._lb[d][xl]

    def initSelf(self):
        self._di = self.argminLB_d()
        self._ID = self._ID + 1
        self._threshold_a = self.getLB()
        self._threshold_b = np.inf

    def getChildContext(self, context: list[AssignmentWithTimestamp], child: IAgent) \
        -> list[AssignmentWithTimestamp]:
        ret_context = []
        child_scp_xi = [a.xi for a in child.scp]
        for asg in copy.deepcopy(context):
            if asg.xi in child_scp_xi:
                ret_context.append(asg)
        return ret_context

    def receive(self, msg: Message):   # received process for each message type
        def receivedValue(msg: Value):
            pre_context = copy.deepcopy(self._CurrentContext)
            self.priorityMerge([msg.asg], self._CurrentContext)
            if not self.isCompatible(pre_context, self._CurrentContext):
                for d in self._D:
                    for child in self._children:
                        if msg.from_xi in [c.xi for c in child.scp]:
                            self.initChild(d, child)
                self.initSelf()
            if msg.from_xi == self._parent.xi:
                self._threshold_a = msg.th_a
                self._threshold_b = msg.th_b
            #self.backTrack()

        def receivedCost(msg: Cost):
            pre_context = copy.deepcopy(self._CurrentContext)
            self.priorityMerge(msg.context, self._CurrentContext)
            if not self.isCompatible(pre_context, self._CurrentContext):
                for d in self._D:
                    for child in self._children:
                        if not self.isCompatible( \
                            self.getChildContext(pre_context, child), self._CurrentContext):
                            self.initChild(d, child)
            if self.isCompatible(msg.context, self._CurrentContext):
                d = self.getAssignment(msg.context, self._xi)
                self._lb[d][msg.xi] = max(self._lb[d][msg.xi], msg.lb)
                self._ub[d][msg.xi] = min(self._ub[d][msg.xi], msg.ub)
            if not self.isCompatible(pre_context, self._CurrentContext):
                self.initSelf()
            #self.backTrack()

        def receivedTerminate(msg: Terminate):
            self._terminate = True
            #self.backTrack()

        if isinstance(msg, Value):
            if self._disp:       # <DISP>
                print("{} receives [VALUE]".format(self._xi))
                print(msg)  ####
            receivedValue(msg)
        elif isinstance(msg, Cost):
            if self._disp:       # <DISP>
                print("{} receives [COST]".format(self._xi))
                print(msg)  #####
            receivedCost(msg)
        elif isinstance(msg, Terminate):
            if self._disp:       # <DISP>
                print("{} receives [TERMINATE]".format(self._xi))
                print(msg)  ####
            receivedTerminate(msg)

    def calcChildThreshold(self, child: IAgent):
        sum_lb_children: float = 0
        for other_child in list(set(self._children) - {child}):
            sum_lb_children = sum_lb_children \
                + self._lb[self._di][other_child.xi]
        return min(self._threshold_b, self.getUB()) \
            - self.delta(self.di) - sum_lb_children

    def argminLB_UB_d(self) -> int:
        lb_d_list = [d for d in self._D if self.LB(d) == self.getLB()]
        return min(lb_d_list, key=self.UB)

    def backTrack(self):
        self.maintainThresholdInvariant()
        pre_di = self._di
        if self._threshold_a == self.getUB():
            self._di = self.argminUB_d()
        elif self.LB(self._di) > self._threshold_a + self._k - 1:
            self._di = self.argminLB_UB_d()
        elif self.LB(self._di) >= min(self._threshold_b, self.getUB()):
            self._di = self.argminLB_UB_d()
        if pre_di != self._di:
            self._ID = self._ID + 1
        self.maintainCurrentValueThreshold()
        self.maintainChildThresholdInvariant()
        self.maintainAllocationInvariant()
        for child in self._children:
            self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID), \
                self._th[self._di][child.xi], self.calcChildThreshold(child)), child)
        for child in list(set(self._lower_neighbor) - set(self._children)):
            self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID), \
                np.inf, np.inf), child)
        if self._threshold_a == self.getUB():
            if self._parent is None or self._terminate:
                for child in self._children:
                    self.send(Terminate(), child)
                self._exec_terminate = True
                return
        self.send(Cost(self._xi, self._CurrentContext, self.getLB(), self.getUB()), self._parent)

    def maintainThresholdInvariant(self):
        LB = self.getLB()
        if self._threshold_a < LB:
            self._threshold_a = LB
        UB = self.getUB()
        if self._threshold_a > UB:
            self._threshold_a = UB

    def maintainAllocationInvariant(self):
        delta = self.delta(self._di)
        sum_t = 0
        for child in self._children:
            sum_t = sum_t + self._th[self._di][child.xi]

        while self._threshold_d[self._di] > delta + sum_t:
            for child in self._children:
                if self._ub[self._di][child.xi] > self._th[self._di][child.xi]:
                    self._th[self._di][child.xi] = self._th[self._di][child.xi] + 1
                    sum_t = sum_t + 1      # because t++
                    #diff = min(self.ub[self.di][child.xi] - self.t[self.di][child.xi],\
                    #            self.threshold - (delta + sum_t))
                    #self.t[self.di][child.xi] = self.t[self.di][child.xi] + diff
                    #sum_t = sum_t + diff
                    break
        while self._threshold_d[self._di] < delta + sum_t:
            for child in self._children:
                if self._th[self._di][child.xi] > self._lb[self._di][child.xi]:
                    self._th[self._di][child.xi] = self._th[self._di][child.xi] - 1
                    sum_t = sum_t - 1      # because t--
                    #diff = min(self.t[self.di][child.xi] - self.lb[self.di][child.xi],\
                    #            (delta + sum_t) - self.threshold)
                    #self.t[self.di][child.xi] = self.t[self.di][child.xi] - diff
                    #sum_t = sum_t - diff
                    break

    def maintainChildThresholdInvariant(self):
        for d in self._D:
            for child in self._children:
                while self._lb[d][child.xi] > self._th[d][child.xi]:
                    self._th[d][child.xi] = self._th[d][child.xi] + 1
        for d in self._D:
            for child in self._children:
                while self._th[d][child.xi] > self._ub[d][child.xi]:
                    self._th[d][child.xi] = self._th[d][child.xi] - 1

    def maintainCurrentValueThreshold(self):
        self._threshold_d[self._di] = self._threshold_a
        if self._threshold_d[self._di] < self.LB(self._di):
            self._threshold_d[self._di] = self.LB(self._di)
        if self._threshold_d[self._di] > self.UB(self._di):
            self._threshold_d[self._di] = self.UB(self._di)