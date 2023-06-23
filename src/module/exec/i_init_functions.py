import abc
from ..util.function import Function
from ..agents.i_agent import IAgent

class IInitFunctions(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        raise NotImplementedError()