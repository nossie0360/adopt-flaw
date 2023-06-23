import copy
import numpy as np

from .message_queue import MessageQueue
from ..i_agent import IAgent
from ...util.assignment import Assignment
from ...util.function import Function
from ...util.abstract_messages import Message, AbstractValue, AbstractCost, AbstractThreshold, AbstractTerminate

class OriginalAgentUtil(IAgent):
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
        self._depth: int = 0
        self._depth_tree: int = 0
        self._message_queue: MessageQueue = MessageQueue()
        self._clock: int = 0
        self._exec_terminate: bool = False
        self._disp: bool = disp
        self._CurrentContext: list[Assignment] = []
        self._lb: dict[int, dict[int, int]] = {}
        self._ub: dict[int, dict[int, int]] = {}

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

    # get Assignment from a context
    def getAssignment(self, context:list[Assignment], xi: int):
        for asg in context:
            if asg.xi == xi:
                return asg.di
        return None

    def addToCurrentContext(self, new_asg: Assignment):
        for asg in self._CurrentContext:
            if asg.xi == new_asg.xi:
                self._CurrentContext.remove(asg)
        self._CurrentContext.append(new_asg)
        return

    def isCompatible(self, context: list[Assignment], CurrentContext: list[Assignment]):
        for asg in context:
            for cur_asg in CurrentContext:
                if asg.xi == cur_asg.xi:
                    if asg.di == cur_asg.di: break
                    else: return False
        return True

    def delta(self, d: int):
        sum: int = 0
        for asg in self._CurrentContext:
            xj = asg.xi
            dj = asg.di
            for fn in self._fset:
                if fn.sp.xi == xj:
                    sum = sum + fn.f(dj, d)
                    break
                elif fn.ep.xi == xj:
                    sum = sum + fn.f(d, dj)
                    break
        return sum

    def LB(self, d):
        sum: int = 0
        for child in self._children:
            xl = child.xi
            sum = sum + self._lb[d][xl]
        return self.delta(d) + sum

    def UB(self, d):
        sum: int = 0
        for child in self._children:
            xl = child.xi
            sum = sum + self._ub[d][xl]
        return self.delta(d) + sum

    def getLB(self):
        LBs = [self.LB(d) for d in self._D]
        return np.min(LBs)

    def getUB(self):
        UBs = [self.UB(d) for d in self._D]
        return np.min(UBs)

    def argminLB_d(self):
        ds = [d for d in self._D]
        LBs = [self.LB(d) for d in self._D]
        return ds[np.argmin(LBs)]

    def argminUB_d(self):
        ds = [d for d in self._D]
        UBs = [self.UB(d) for d in self._D]
        return ds[np.argmin(UBs)]

    def processMessage(self):
        if self.message_queue.isEmpty() or self.isTerminated():
            return False
        msg = self.message_queue.pop(0)
        self.receive(msg)
        if self.message_queue.isEmpty():
            self.backTrack()
        return True

    def send(self, msg: Message, dst_agent: IAgent):
        if dst_agent is None: return

        # <DISP>
        if self._disp:
            mtype = ""
            if isinstance(msg, AbstractValue):
                mtype = "VALUE"
            elif isinstance(msg, AbstractCost):
                mtype = "COST"
            elif isinstance(msg, AbstractThreshold):
                mtype = "THRESHOLD"
            elif isinstance(msg, AbstractTerminate):
                mtype = "TERMINATE"
            print("[{}] {} -> {} : ".format(mtype, self._xi, dst_agent.xi), msg)
        # </DISP>

        msg.from_xi = self._xi
        msg.sent_clock = self._clock
        dst_agent.addMessage(copy.deepcopy(msg))