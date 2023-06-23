from .i_agent import IAgent
from .idb_adopt.idb_agent import IdbAgent
from .util.classified_message_queue import ClassifiedMessageQueue
from .util.message_queue import MessageQueue
from ..util.abstract_messages import Message
from ..util.function import Function

# Agent whose message queue is classified sender.
class MsgClassifyAgentWrapper(IAgent):
    def __init__(self, agent: IAgent):
        self._base_agent = agent
        self._base_agent.message_queue = ClassifiedMessageQueue()

    @property
    def base_agent(self):
        return self._base_agent

    @property
    def xi(self) -> int:
        return self._base_agent.xi

    @property
    def di(self) -> int:
        return self._base_agent.di

    @property
    def D(self) -> list[int]:
        return self._base_agent.D

    @property
    def fset(self) -> list[Function]:
        return self._base_agent.fset

    @property
    def parent(self) -> "IAgent":
        return self._base_agent.parent

    @parent.setter
    def parent(self, p: "IAgent"):
        self._base_agent.parent = p

    @property
    def children(self) -> list["IAgent"]:
        return self._base_agent.children

    @property
    def neighbor(self) -> list["IAgent"]:
        return self._base_agent.neighbor

    @property
    def lower_neighbor(self) -> list["IAgent"]:
        return self._base_agent.lower_neighbor

    @property
    def ancestors(self) -> list["IAgent"]:
        return self._base_agent.ancestors

    @ancestors.setter
    def ancestors(self, ancestors: list["IAgent"]):
        self._base_agent.ancestors = ancestors

    @property
    def scp(self) -> list["IAgent"]:
        """
        a set of ancestors which share a constrant with the agent or its descendant.
        """
        return self._base_agent.scp

    @scp.setter
    def scp(self, s: list["IAgent"]):
        self._base_agent.scp = s

    @property
    def all_agents(self) -> list["IAgent"]:
        return self._base_agent.all_agents

    @all_agents.setter
    def all_agents(self, all_agents: list["IAgent"]):
        self._base_agent.all_agents = all_agents

    @property
    def depth(self) -> int:
        return self._base_agent.depth

    @depth.setter
    def depth(self, d: int):
        self._base_agent.depth = d

    @property
    def depth_tree(self) -> int:
        return self._base_agent.depth_tree

    @depth_tree.setter
    def depth_tree(self, d: int):
        self._base_agent.depth_tree = d

    @property
    def message_queue(self) -> ClassifiedMessageQueue:
        return self._base_agent.message_queue

    @message_queue.setter
    def message_queue(self, msg_queue: ClassifiedMessageQueue):
        self._base_agent.message_queue = msg_queue

    def addFuntion(self, f: Function):
        """
        add a function to the agent.
        """
        return self._base_agent.addFuntion(f)

    def getMessageQueueLength(self) -> int:
        """
        return the length of the message queue of the agent.
        """
        return self._base_agent.message_queue.getLength()

    def isTerminated(self) -> bool:
        """
        return whether the agents is terminated or not.
        """
        return self._base_agent.isTerminated()

    def initializeMessageQueue(self):
        return self._base_agent.message_queue.\
            initializeMessageQueue(self._base_agent.neighbor)

    def initialize(self):
        return self._base_agent.initialize()

    def initialize_idb(self, root_threshold: int):
        if not isinstance(self._base_agent, IdbAgent):
            raise ValueError("{} (xi={}) is not IdbAgent."\
                             .format(self._base_agent, self._base_agent.xi))
        if self._base_agent.parent is None:
            return self._base_agent.initialize_root(root_threshold)
        else:
            return self._base_agent.initialize()


    def addMessage(self, msg: Message):
        return self._base_agent.message_queue.addMessage(msg)

    def updateMessageQueue(self, targets: list[IAgent]=[]):
        """
        Args:
            targets (list[Agent]): the queue sent from this updated (defalut: all involved agents)
        """
        if len(targets) == 0:
            agents_id = self.getInvolvedAgentsId()
            targets = [agent for agent in self._base_agent.all_agents if agent.xi in agents_id]
        return self._base_agent.message_queue.updateMessageQueue(targets)

    def updateMessageQueueTypeConditioned(self, msg_type: type, targets: list[IAgent]=[]):
        """
        Update queue until a message whose type equals to the msg_type is found
        in the unreached queue (condition_msg is NOT ADDED).
        Args:
            targets (list[Agent]): the queue sent from this updated (defalut: all neighbor)
        """
        if len(targets) == 0:
            agents_id = self.getInvolvedAgentsId()
            targets = [agent for agent in self._base_agent.all_agents if agent.xi in agents_id]
        return self._base_agent.message_queue.updateMessageQueueTypeConditioned(targets, msg_type)

    def updateMessageQueueTimeConditioned(self, clock_time: int = None,
                                          targets: list[IAgent]=[]):
        """
        add messages in unreached_queue sent until clock_time to reached_queue.
        (NOT removing any messages)

        Args:
            clock_time (int): the time to add messages.
            If any number is not given, all messages are added.

        Note:
            We assume that unreached_queue is sorted in chronological order.
        """
        if len(targets) == 0:
            agents_id = self.getInvolvedAgentsId()
            targets = [agent for agent in self._base_agent.all_agents if agent.xi in agents_id]
        return self._base_agent.message_queue.\
            updateMessageQueueTimeConditioned(targets, clock_time)

    def getInvolvedAgentsId(self) -> list[int]:
        return self._base_agent.message_queue.getQueueKeys()

    def backTrack(self):
        return self._base_agent.backTrack()

    def setClock(self, clock_time: int = None):
        return self._base_agent.setClock(clock_time)

    # if message_queue is empty or agent is terminated, return False
    def processMessage(self, from_xi: int):
        if self._base_agent.message_queue.isEmpty(from_xi) or self.isTerminated():
            return False
        msg = self._base_agent.message_queue.pop(0, from_xi)
        self._base_agent.receive(msg)
        if all([self._base_agent.message_queue.isEmpty(xi)
                for xi in self.getInvolvedAgentsId()]):
            self._base_agent.backTrack()
        return True

    def send(self, msg: Message, dst: IAgent) -> None:
        """
        send a message.
        """
        self._base_agent.send(msg, dst)

    def receive(self, msg: Message) -> None:
        """
        receive a message.
        """
        self._base_agent.receive(msg)