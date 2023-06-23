import abc
from ..agents.i_agent import IAgent

class IInitAgents(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def __init__(self, agent_class: type):
        pass

    @abc.abstractclassmethod
    def getAgents(self) -> list[IAgent]:
        raise NotImplementedError()