from .exec_cycle import ExecCycle
from .init_agents import InitAgents
from .init_functions import InitFunctions
from ...i_exec_collection import IExecCollection

class TerminationWithoutRedundantExec(IExecCollection):
    def __init__(self, agent_class: type):
        self._exec_cycle = ExecCycle(agent_class)
        self._init_agents = InitAgents(agent_class)
        self._init_functions = InitFunctions()

    @property
    def exec_cycle(self):
        return self._exec_cycle

    @property
    def init_agents(self):
        return self._init_agents

    @property
    def init_functions(self):
        return self._init_functions