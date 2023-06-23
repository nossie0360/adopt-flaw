from .init_agents import InitAgents
from .init_functions import InitFunctions
from ..util.basic_exec_cycle import BasicExecCycle
from src.module.exec.i_exec_collection import IExecCollection

class AdoptExampleGraphExec(IExecCollection):
    def __init__(self, agent_class: type):
        self._exec_cycle = BasicExecCycle(agent_class)
        self._init_agents = InitAgents(agent_class)
        self._init_functions = InitFunctions()
        self._optimal_solution = [1, 1, 1, 1]
        self._optimal_cost = 4

    @property
    def exec_cycle(self):
        return self._exec_cycle

    @property
    def init_agents(self):
        return self._init_agents

    @property
    def init_functions(self):
        return self._init_functions

    @property
    def optimal_solution(self):
        return self._optimal_solution

    @property
    def optimal_cost(self):
        return self._optimal_cost