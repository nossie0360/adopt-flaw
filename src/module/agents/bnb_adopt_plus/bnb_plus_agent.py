import copy
import numpy as np

from .messages_bnb_plus import Value, Cost, Terminate
from ..i_agent import IAgent
from ..bnb_adopt.bnb_agent import BnbAgent
from ...util.abstract_messages import Message
from ...util.assignment_with_timestamp import AssignmentWithTimestamp

class BnbPlusAgent(BnbAgent):
    def __init__(self, xi: int, di: int, D: int, disp: bool = True):
        super().__init__(xi, di, D, disp)

    # ADOPT implement
    def initialize(self):
        self._exec_terminate: bool = False
        self._terminate: bool = False
        self._threshold: float = 0
        self._CurrentContext: list[AssignmentWithTimestamp] = \
            [AssignmentWithTimestamp(na.xi, 0, 0) for na in self._scp]
        self._ID: int = 0
        self._lb: dict[int, dict[int, float]] = {}
        self._ub: dict[int, dict[int, float]] = {}
        for d in self._D:
            self._lb[d] = {}; self._ub[d] = {}
            for child in self._children:
                self.initChild(d, child)
        self.initSelf()
        self._is_context_changed = True
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

    def initSelf(self):
        self._di = self.argminLB_d()
        self._ID = self._ID + 1
        self._threshold = np.inf
        self._is_threshold_initialized = True

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
                self._threshold = msg.th

            if not self.isSameContext(pre_context, self._CurrentContext):
                self._is_context_changed = True
            #self.backTrack()

        def receivedCost(msg: Cost):
            self._last_received_cost_messages[msg.from_xi] = copy.deepcopy(msg)
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

            if not self.isSameContext(pre_context, self._CurrentContext):
                self._is_context_changed = True
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

    def backTrack(self):
        if self.LB(self._di) >= min(self._threshold, self.getUB()) \
            and self.LB(self._di) != self.getLB():
            self._di = self.argminLB_d()
            self._ID = self._ID + 1
        if (self.parent is None and self.getUB() <= self.getLB()) \
            or self._terminate:
            for child in self._children:
                self.send(Terminate(), child)
            self._exec_terminate = True
            return
        for child in self._children:
            self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID), \
                self.calcChildThreshold(child)), child)
        for lower in list(set(self._lower_neighbor) - set(self.children)):
            self.send(Value(AssignmentWithTimestamp(self._xi, self._di, self._ID), np.inf), lower)
        self.send(Cost(self.xi, self._CurrentContext, self.getLB(), self.getUB(), self.getThReq()), \
            self._parent)
        self._is_context_changed = False
        self._is_threshold_initialized = False

    def getThReq(self):
        return self._is_threshold_initialized

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