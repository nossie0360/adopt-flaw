import copy
import numpy as np
from ..i_agent import IAgent
from ..util.timestamp_agent_util import TimestampAgentUtil
from ..util.message_queue import MessageQueue
from ...util.assignment_with_timestamp import AssignmentWithTimestamp
from ...util.abstract_messages import Message
from .messages_plus import Value, Cost, Terminate

class PlusAgent(TimestampAgentUtil):
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    # ADOPT implement
    def initialize(self):
        self._exec_terminate = False
        self._terminate = False
        self._threshold = 0
        self._CurrentContext = []
        self._lb = {}; self._ub = {}; self._t = {}; self._context = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}; self._t[d] = {}; self._context[d] = {}
            for child in self._children:
                xl = child.xi
                self._lb[d][xl] = 0
                self._ub[d][xl] = np.inf
                self._t[d][xl] = 0
                self._context[d][xl] = []
        self._di = self.argminLB_d()

        self._ID = 1
        self._is_context_changed = True
        self._is_threshold_not_copied = False
        self._is_threshold_initialized = True
        self._last_sent_value_messages: dict[int, Value] = {}
        self._last_sent_cost_messages: dict[int, Cost] = {}
        self._last_received_cost_messages: dict[int, Cost] = {}
        self._replied_last_cost_message: dict[int, bool] = {}
        for n_agent in self._neighbor:
            self._last_sent_value_messages[n_agent.xi] = None
            self._last_sent_cost_messages[n_agent.xi] = None
            self._last_received_cost_messages[n_agent.xi] = None
            self._replied_last_cost_message[n_agent.xi] = False

        self.backTrack()

    def receive(self, msg: Message):   # received process for each message type
        def receivedValue(msg: Value):
            if self._terminate: return
            pre_context = copy.deepcopy(self._CurrentContext)
            if self.getAssignment(self._CurrentContext, msg.from_xi) is None:
                self.addToCurrentContext(msg.asg)
            else:
                self.priorityMerge([msg.asg], self._CurrentContext)
            if msg.from_xi == self._parent.xi:
                self.priorityMerge(msg.context, self._CurrentContext)
                if self.isCompatible(msg.context, self._CurrentContext):
                    self._threshold = msg.t
                    self._is_threshold_not_copied = False
                else:
                    self._is_threshold_not_copied = True

            if not self.isSameContext(pre_context, self._CurrentContext):
                self._is_context_changed = True
                self._is_threshold_initialized = True

            for d in self._D:
                for child in self._children:
                    xl = child.xi
                    if not self.isCompatible(self._context[d][xl], self._CurrentContext):
                        self._lb[d][xl] = 0
                        self._t[d][xl] = 0
                        self._ub[d][xl] = np.inf
                        self._context[d][xl] = []

            self.maintainThresholdInvariant()
            #self.backTrack()

        def receivedCost(msg: Cost):
            self._last_received_cost_messages[msg.from_xi] = copy.deepcopy(msg)
            self._replied_last_cost_message[msg.from_xi] = False
            d = None
            for asg in msg.context:
                if asg.xi == self._xi:
                    d = asg.di
                    msg.context.remove(asg)

            if not self._terminate:
                pre_context = copy.deepcopy(self._CurrentContext)
                for asg in msg.context:
                    if self.getAssignment(self._CurrentContext, asg.xi) is None:
                        self.addToCurrentContext(asg)
                self.priorityMerge(msg.context, self._CurrentContext)
                for dp in self._D:
                    for child in self._children:
                        xl = child.xi
                        if not self.isCompatible(self._context[dp][xl], self._CurrentContext):
                            self._lb[dp][xl] = 0
                            self._t[dp][xl] = 0
                            self._ub[dp][xl] = np.inf
                            self._context[dp][xl] = []
                if not self.isSameContext(pre_context, self._CurrentContext):
                    self._is_context_changed = True
                    self._is_threshold_initialized = True

            if self.isCompatible(msg.context, self._CurrentContext) and d is not None:
                self._lb[d][msg.xi] = msg.lb
                self._ub[d][msg.xi] = msg.ub
                self._context[d][msg.xi] = msg.context
                self.maintainChildThresholdInvariant()
                self.maintainThresholdInvariant()
            #self.backTrack()

        def receivedTerminate(msg: Terminate):
            self._terminate = True
            self._CurrentContext = msg.context
            self.maintainThresholdInvariant() # NOT in the original, but need for stop.
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

    def backTrack(self):
        pre_di = self._di
        if self._threshold == self.getUB():
            self._di = self.argminUB_d()
        elif self.LB(self._di) > self._threshold:
            self._di = self.argminLB_d()
        if pre_di != self._di:
            self._ID = self._ID + 1
        self.maintainAllocationInvariant()
        for dst in self._lower_neighbor:
            if dst in self._children:
                self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID),
                                self._t[self._di][dst.xi], self._CurrentContext), dst)
            else:
                self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID),
                                0, self._CurrentContext), dst)

        if self._threshold == self.getUB():
            if self._terminate or self._parent is None:
                for dst in self._children:
                    self.send(Terminate( self._CurrentContext +\
                        [AssignmentWithTimestamp(self._xi, self._di, self._ID)] ), dst)
                self._exec_terminate = True
                return
        self.send(Cost(self._xi, self._CurrentContext, self.getLB(), self.getUB(),
                       self.getThReq()), self._parent)
        self._is_context_changed = False
        self._is_threshold_initialized = False

    def maintainThresholdInvariant(self):
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

    def maintainChildThresholdInvariant(self):
        for d in self._D:
            for child in self._children:
                while self._lb[d][child.xi] > self._t[d][child.xi]:
                    self._t[d][child.xi] = self._t[d][child.xi] + 1
        for d in self._D:
            for child in self._children:
                while self._t[d][child.xi] > self._ub[d][child.xi]:
                    self._t[d][child.xi] = self._t[d][child.xi] - 1

    def getThReq(self):
        return self._is_threshold_not_copied or self._is_threshold_initialized

    def isSameContext(self, context_1: list[AssignmentWithTimestamp],
                      context_2: list[AssignmentWithTimestamp]) -> bool:
        asg_xi_1 = {asg.xi for asg in context_1}
        asg_xi_2 = {asg.xi for asg in context_2}
        return asg_xi_1 == asg_xi_2 and self.isCompatible(context_1, context_2)

    def isRedundant(self, msg: Message, dst_agent: IAgent) -> bool:
        if isinstance(msg, Value):
            last_msg = copy.deepcopy(self._last_sent_value_messages[dst_agent.xi])
            if self._last_received_cost_messages[dst_agent.xi] is None:
                received_th_req = False
            else:
                if not self._replied_last_cost_message[dst_agent.xi]:
                    received_th_req = self._last_received_cost_messages[dst_agent.xi].th_req
                    self._replied_last_cost_message[dst_agent.xi] = True
                else:
                    received_th_req = False
            return last_msg is not None \
                and msg.asg.di == last_msg.asg.di \
                and not received_th_req
        elif isinstance(msg, Cost):
            last_msg = copy.deepcopy(self._last_sent_cost_messages[dst_agent.xi])
            return last_msg is not None \
                and self.isSameContext(msg.context, last_msg.context) \
                and msg.lb == last_msg.lb and msg.ub == last_msg.ub \
                and not self._is_context_changed
        else:
            return False

    def send(self, msg: Message, dst_agent: IAgent):
        if dst_agent is None: return

        if not self.isRedundant(msg, dst_agent):
            msg.from_xi = self._xi
            msg.sent_clock = self._clock
            dst_agent.addMessage(copy.deepcopy(msg))
            if isinstance(msg, Value):
                self._last_sent_value_messages[dst_agent.xi] = copy.deepcopy(msg)
            elif isinstance(msg, Cost):
                self._last_sent_cost_messages[dst_agent.xi] = copy.deepcopy(msg)

            # <DISP>
            if self._disp:
                mtype = ""
                if isinstance(msg, Value):
                    mtype = "VALUE"
                elif isinstance(msg, Cost):
                    mtype = "COST"
                elif isinstance(msg, Terminate):
                    mtype = "TERMINATE"
                print("[{}] {} -> {} : ".format(mtype, self._xi, dst_agent.xi), msg)
            # </DISP>