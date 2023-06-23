import copy
import numpy as np
import enum
from typing import Literal

from .messages_bd import Value, Cost, Terminate, RealTree
from ..util.timestamp_agent_util import TimestampAgentUtil
from ..i_agent import IAgent
from ...util.abstract_messages import Message
from ...util.assignment_with_timestamp import AssignmentWithTimestamp

class BdAgent(TimestampAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    class Method(enum.Enum):
        DFS = enum.auto()
        BFS = enum.auto()

    # ADOPT implement
    def initialize(self):
        self._exec_terminate: bool = False
        self._terminate: bool = False
        self._alpha = 0.5
        self._chain_tree: int = 0
        self._method: Literal[self.Method.DFS, self.Method.BFS] = None
        self._is_top_layer_bfs: bool = False
        self.preprocessing()
        self.chooseMethod()

        self._threshold: float = 0
        self._threshold_s: float = 0
        self._CurrentContext: list[AssignmentWithTimestamp] = \
            [AssignmentWithTimestamp(na.xi, 0, 0) for na in self._scp]
        self._ID: int = 0
        self._lb: dict[int, dict[int, float]] = {}
        self._ub: dict[int, dict[int, float]] = {}
        self._t: dict[int, dict[int, float]] = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}; self._t[d] = {}
            for child in self._children:
                self.initChild(d, child)
        self.initSelf()
        self.backTrack()

    def initChild(self, d: int, child: IAgent):
        xl = child.xi
        self._lb[d][xl] = 0
        self._ub[d][xl] = np.inf
        self._t[d][xl] = self._lb[d][xl]

    def initSelf(self):
        self._di = self.argminLB_d()
        self._ID = self._ID + 1
        if self._method == self.Method.DFS:         # not in the paper
            self._threshold = np.inf
        elif self._is_top_layer_bfs:
            self._threshold_s = np.inf
            self._threshold = self.getLB()
        else:
            self._threshold = self.getLB()

    def preprocessing(self):
        self._chain_tree = 0
        while True:
            self.updateMessageQueue()
            if self.parent is None:
                if(len(self._children) > 1):
                    for child in self.children:
                        self.send(RealTree(True, self._chain_tree), child)
                    break
                else:
                    self._method = self.Method.DFS
                    for child in self.children:
                        self.send(RealTree(False, self._chain_tree + 1), child)
                    break
            if not self.message_queue.isEmpty():
                msg = self.message_queue.pop(0)
                self.receive(msg)
                break

    def chooseMethod(self):
        if self._method is not None:
            return
        real_depth_tree = self._depth_tree - self._chain_tree
        depth_layer_p = int(self._alpha * real_depth_tree)
        depth_layer = self._chain_tree + depth_layer_p
        if self._depth < depth_layer:
            self._method = self.Method.DFS
        else:
            self._method = self.Method.BFS
            if self._depth == depth_layer:
                self._is_top_layer_bfs = True
            else:
                self._is_top_layer_bfs = False

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
                if self._is_top_layer_bfs:
                    self._threshold_s = msg.th
                else:
                    self._threshold = msg.th
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

        def receivedRealTree(msg: RealTree):
            mark = msg.mark
            if msg.mark:
                self._chain_tree = msg.chain_tree
            else:
                if len(self._children) > 1:
                    mark = True
                    self._chain_tree = msg.chain_tree
                else:
                    self._method = self.Method.DFS
                    self._chain_tree = msg.chain_tree + 1
            for child in self.children:
                self.send(RealTree(mark, self._chain_tree), child)

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
        elif isinstance(msg, RealTree):
            if self._disp:       # <DISP>
                print("{} receives [RealTree]".format(self._xi))
                print(msg)  #####
            receivedRealTree(msg)

    def backTrack(self):
        self.maintainThresholdInvariant()
        pre_di = self._di
        if self._method == self.Method.BFS:
            if self._threshold == self.getUB()\
                and self.UB(self.di) != self.getUB():
                self._di = self.argminUB_d()
            elif self._is_top_layer_bfs \
                and self.LB(self._di) > min(self._threshold, self._threshold_s):
                self._di = self.argminLB_d()
            elif self.LB(self._di) > self._threshold:
                self._di = self.argminLB_d()
        else:
            if self._terminate and self._threshold == self.getUB() \
                and self.UB(self._di) != self.getUB():
                self._di = self.argminUB_d()
            elif self.LB(self._di) >= self._threshold \
                and self.LB(self._di) != self.getLB():
                self._di = self.argminLB_d()
        if self._di != pre_di:
            self._ID = self._ID + 1
        self.maintainChildThresholdInvariant()
        self.maintainAllocationInvariant()
        if self._method == self.Method.DFS:
            if self._threshold <= self.getLB() \
                and (self._parent is None or self._terminate):
                for child in self._children:
                    self.send(Terminate(), child)
                self._exec_terminate = True
                return
        else:
            if self._terminate:
                if (self._is_top_layer_bfs and self._threshold_s == self.getUB()) \
                    or self._threshold == self.getUB():
                    for child in self._children:
                        self.send(Terminate(), child)
                    self._exec_terminate = True
        for child in self._children:
            self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID),
                            self._t[self._di][child.xi]), child)
        for p_child in self._lower_neighbor:
            if p_child not in self._children:
                self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID),
                                np.inf), p_child)
        self.send(Cost(self._xi, self._CurrentContext, self.getLB(), self.getUB()),
                  self._parent)

    def maintainThresholdInvariant(self):
        if self._threshold < self.getLB():
            self._threshold = self.getLB()
        if self._threshold > self.getUB():
            self._threshold = self.getUB()
        if self._is_top_layer_bfs:
            if self._threshold_s < self.getLB():        # As for LB, not in the paper
                self._threshold_s = self.getLB()
            if self._threshold_s > self.getUB():
                self._threshold_s = self.getUB()

    def maintainAllocationInvariant(self):
        delta = self.delta(self._di)
        if self._method == self.Method.DFS:
            for child in self._children:
                if self._terminate and self.getUB() == self._threshold:
                    sum_ub = sum(self._ub[self._di].values()) \
                        - self._ub[self._di][child.xi]
                    self._t[self._di][child.xi] = self._threshold - delta - sum_ub
                else:
                    sum_lb = sum(self._lb[self._di].values()) \
                        - self._lb[self._di][child.xi]
                    self._t[self._di][child.xi] = self._threshold - delta - sum_lb
        else:
            if self._is_top_layer_bfs:
                sum_t = sum(self._t[self._di].values())
                while min(self._threshold_s, self._threshold) > delta + sum_t:
                    for child in self._children:
                        if self._ub[self._di][child.xi] > self._t[self._di][child.xi]:
                            self._t[self._di][child.xi] = self._t[self._di][child.xi] + 1
                            sum_t = sum_t + 1      # because t++
                            break
                while min(self._threshold_s, self._threshold) < delta + sum_t:
                    for child in self._children:
                        if self._t[self._di][child.xi] > self._lb[self._di][child.xi]:
                            self._t[self._di][child.xi] = self._t[self._di][child.xi] - 1
                            sum_t = sum_t - 1      # because t--
                            break
            else:
                sum_t = sum(self._t[self._di].values())
                while self._threshold > delta + sum_t:
                    for child in self._children:
                        if self._ub[self._di][child.xi] > self._t[self._di][child.xi]:
                            self._t[self._di][child.xi] = self._t[self._di][child.xi] + 1
                            sum_t = sum_t + 1      # because t++
                            break
                while self._threshold < delta + sum_t:
                    for child in self._children:
                        if self._t[self._di][child.xi] > self._lb[self._di][child.xi]:
                            self._t[self._di][child.xi] = self._t[self._di][child.xi] - 1
                            sum_t = sum_t - 1      # because t--
                            break

    def maintainChildThresholdInvariant(self):
        #for d in self._D:
        #    for child in self._children:
        #        while self._lb[d][child.xi] > self._t[d][child.xi]:
        #            self._t[d][child.xi] = self._t[d][child.xi] + 1
        #for d in self._D:
        #    for child in self._children:
        #        while self._t[d][child.xi] > self._ub[d][child.xi]:
        #            self._t[d][child.xi] = self._t[d][child.xi] - 1
        for d in self._D:                   # not in the paper
            for child in self._children:
                if self._lb[d][child.xi] > self._t[d][child.xi]:
                    self._t[d][child.xi] = self._lb[d][child.xi]
                if self._t[d][child.xi] > self._ub[d][child.xi]:
                    self._t[d][child.xi] = self._ub[d][child.xi]