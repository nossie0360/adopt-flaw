from __future__ import annotations
import abc

from ..util.function import Function
from ..util.abstract_messages import Message
from .util.message_queue import MessageQueue

class IAgent(metaclass=abc.ABCMeta):
    """
    Interface of the agent.
    """
    @property
    @abc.abstractmethod
    def xi(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def di(self) -> int:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def D(self) -> list[int]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def fset(self) -> list[Function]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def parent(self) -> "IAgent":
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def children(self) -> list["IAgent"]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def neighbor(self) -> list["IAgent"]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def lower_neighbor(self) -> list["IAgent"]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def ancestors(self) -> list["IAgent"]:
        raise NotImplementedError()

    @ancestors.setter
    @abc.abstractmethod
    def ancestors(self, ancestors: list["IAgent"]):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def scp(self) -> list["IAgent"]:
        """
        a set of ancestors which share a constrant with the agent or its descendant.
        """
        raise NotImplementedError()

    @scp.setter
    @abc.abstractmethod
    def scp(self, s: list["IAgent"]):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def all_agents(self) -> list["IAgent"]:
        raise NotImplementedError()

    @all_agents.setter
    @abc.abstractmethod
    def all_agents(self, all_agents: list["IAgent"]):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def depth(self) -> int:
        raise NotImplementedError()

    @depth.setter
    @abc.abstractmethod
    def depth(self, d: int):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def depth_tree(self) -> int:
        raise NotImplementedError()

    @depth_tree.setter
    @abc.abstractmethod
    def depth_tree(self, d: int):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def message_queue(self) -> MessageQueue:
        raise NotImplementedError()

    @message_queue.setter
    @abc.abstractmethod
    def message_queue(self, msg_queue: MessageQueue):
        raise NotImplementedError()

    @abc.abstractmethod
    def initialize(self):
        """
        ADOPT's initialize
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def backTrack(self):
        """
        ADOPT's backtrack
        """
        #raise NotImplementedError()

    @abc.abstractmethod
    def setClock(self, clock_time: int = None):
        """
        set the clock of the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def addFuntion(self, f: Function):
        """
        add a function to the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def addMessage(self, msg: Message):
        """
        add a message to the unreached message queue of the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def updateMessageQueue(self):
        """
        update the message queue of the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def processMessage(self):
        """
        process all messages in the message queue of the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def getMessageQueueLength(self) -> int:
        """
        return the length of the message queue of the agent.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def isTerminated(self) -> bool:
        """
        return whether the agents is terminated or not.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def send(self, msg: Message, dst_agent: IAgent) -> None:
        """
        send a message.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def receive(self, msg: Message) -> None:
        """
        receive a message.
        """
        raise NotImplementedError()