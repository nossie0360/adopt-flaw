import copy
import numpy as np

from ..i_agent import IAgent
from ..util.message_queue import MessageQueue
from ..util.original_agent_util import OriginalAgentUtil
from ...util.assignment import Assignment
from ...util.abstract_messages import Message
from .messages import Value, Cost, Threshold, Terminate

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...util.function import Function

class ModifiedAgent(OriginalAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool=True):
        super().__init__(xi, di, D, disp)

    # ADOPT implement
    def initialize(self):
        self._exec_terminate: bool = False
        self._terminate: bool = False
        self._threshold: float = 0
        self._b = 0
        if self._parent is None:
            self._threshold = self._b
        self._CurrentContext: list[Assignment] = \
            [Assignment(na.xi, 0) for na in self._scp]
        self._lb: dict[int, dict[int, float]] = {}
        self._ub: dict[int, dict[int, float]] = {}
        self._t: dict[int, dict[int, float]] = {}
        self._context: dict[int, dict[int, list[Assignment]]] = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}; self._t[d] = {}; self._context[d] = {}
            for child in self._children:
                self.initChild(d, child)
        self._di = self.argminLB_d()
        self.maintainThresholdInvariant()
        self.backTrack()

    def initChild(self, d: int, child: IAgent):
        xl = child.xi
        self._lb[d][xl] = 0
        self._ub[d][xl] = np.inf
        self._t[d][xl] = 0
        self._context[d][xl] = []

    def receive(self, msg: Message):   # received process for each message type
        def receivedValue(msg: Value):
            if self._terminate: return
            self.addToCurrentContext(msg.asg)
            for d in self._D:
                for child in self._children:
                    xl = child.xi
                    if not self.isCompatible(self._context[d][xl], self._CurrentContext):
                        self.initChild(d, child)
            self.maintainThresholdInvariant()
            #self.backTrack()

        def receivedCost(msg: Cost):
            d = None
            for asg in msg.context:
                if asg.xi == self._xi:
                    d = asg.di
                    msg.context.remove(asg)

            if not self._terminate:
                neighbor_xi_list = [n_agent.xi for n_agent in self._neighbor]
                for asg in msg.context:
                    if asg.xi not in neighbor_xi_list:
                        self.addToCurrentContext(asg)
                for dp in self._D:
                    for child in self._children:
                        xl = child.xi
                        if not self.isCompatible(self._context[dp][xl], self._CurrentContext):
                            self.initChild(dp, child)

            if self.isCompatible(msg.context, self._CurrentContext) and d is not None:
                self._lb[d][msg.xi] = max(self._lb[d][msg.xi], msg.lb)
                self._ub[d][msg.xi] = min(self._ub[d][msg.xi], msg.ub)
                self._context[d][msg.xi] = msg.context
                self.maintainChildThresholdInvariant()
                self.maintainThresholdInvariant()
            #self.backTrack()

        def receivedThreshold(msg: Threshold):
            if self.isCompatible(msg.context, self._CurrentContext):
                self._threshold = msg.t
                self.maintainThresholdInvariant()
                #self.backTrack()

        def receivedTerminate(msg: Terminate):
            self._terminate = True
            #if not self.isCompatible(self._CurrentContext, msg.context):
            #    self._threshold = 0
            self._CurrentContext = msg.context
            self._threshold = msg.t
            for dp in self._D:
                    for child in self._children:
                        xl = child.xi
                        if not self.isCompatible(self._context[dp][xl], self._CurrentContext):
                            self.initChild(dp, child)
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
        elif isinstance(msg, Threshold):
            if self._disp:       # <DISP>
                print("{} receives [THRESHOLD]".format(self._xi))
                print(msg)  ####
            receivedThreshold(msg)
        elif isinstance(msg, Terminate):
            if self._disp:       # <DISP>
                print("{} receives [TERMINATE]".format(self._xi))
                print(msg)  ####
            receivedTerminate(msg)


    def backTrack(self):
        if self._threshold == self.getUB()\
            and self.UB(self._di) != self.getUB():
            self._di = self.argminUB_d()
        elif self.LB(self._di) > self._threshold:
            self._di = self.argminLB_d()
        for dst in self._lower_neighbor:
            self.send(Value(Assignment(self._xi, self._di)), dst)

        self.maintainAllocationInvariant()
        if self._threshold == self.getUB():
            if self._terminate or self._parent is None:
                for dst in self._children:
                    self.send(Terminate(self._t[self.di][dst.xi], self._CurrentContext +\
                        [Assignment(self._xi, self._di)] ), dst)
                self._exec_terminate = True
                return
        self.send(Cost(self._xi, self._CurrentContext, self.getLB(), self.getUB()), self._parent)

    def maintainThresholdInvariantRoot(self):
        self._threshold = min(self.getLB() + self._b, self.getUB())

    def maintainThresholdInvariant(self):
        if self._parent is None and self._b > 0:
            self.maintainThresholdInvariantRoot()
            return
        LB = self.getLB()
        if self._threshold < LB:
            self._threshold = LB
        UB = self.getUB()
        if self._threshold > UB:
            self._threshold = UB


    def maintainAllocationInvariant(self):
        delta = self.delta(self._di)
        sum_t = 0
        for child in self._children:
            sum_t = sum_t + self._t[self._di][child.xi]

        while self._threshold > delta + sum_t:
            for child in self._children:
                if self._ub[self._di][child.xi] > self._t[self._di][child.xi]:
                    self._t[self._di][child.xi] = self._t[self._di][child.xi] + 1
                    sum_t = sum_t + 1      # because t++
                    #diff = min(self._ub[self._di][child.xi] - self._t[self._di][child.xi],\
                    #            self._threshold - (delta + sum_t))
                    #self._t[self._di][child.xi] = self._t[self._di][child.xi] + diff
                    #sum_t = sum_t + diff
                    break
        while self._threshold < delta + sum_t:
            for child in self._children:
                if self._t[self._di][child.xi] > self._lb[self._di][child.xi]:
                    self._t[self._di][child.xi] = self._t[self._di][child.xi] - 1
                    sum_t = sum_t - 1      # because t--
                    #diff = min(self._t[self._di][child.xi] - self._lb[self._di][child.xi],\
                    #            (delta + sum_t) - self._threshold)
                    #self._t[self._di][child.xi] = self._t[self._di][child.xi] - diff
                    #sum_t = sum_t - diff
                    break
        for dst in self._children:
            self.send(Threshold(self._t[self._di][dst.xi], self._CurrentContext), dst)

    def maintainChildThresholdInvariant(self):
        for d in self._D:
            for child in self._children:
                while self._lb[d][child.xi] > self._t[d][child.xi]:
                    self._t[d][child.xi] = self._t[d][child.xi] + 1
        for d in self._D:
            for child in self._children:
                while self._t[d][child.xi] > self._ub[d][child.xi]:
                    self._t[d][child.xi] = self._t[d][child.xi] - 1