import abc

class IExecCollection(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, agent_class: type):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def exec_cycle(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def init_agents(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def init_functions(self):
        raise NotImplementedError()