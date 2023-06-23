import copy

from src.module.agents.i_agent import IAgent
from src.module.util.dfs import DFS
from src.module.util.function import Function
from src.module.exec.i_init_agents import IInitAgents
from src.module.exec.i_init_functions import IInitFunctions
from src.module.exec.i_exec_cycle import IExecCycle

class ExecutionManagerForTest():
    def __init__(self, init_agents: IInitAgents, init_functions: IInitFunctions,
                 exec_cycle: IExecCycle) -> None:
        self.init_agents = init_agents
        self.init_functions = init_functions
        self.exec_cycle = exec_cycle

    def addFunctionsToAgents(self, agents: list[IAgent], functions: list[Function]):
        for f in functions:
            agents[f.sp.xi].addFuntion(f)
            agents[f.ep.xi].addFuntion(f)

    def getFinalSolutionAndCost(self, agents: list[IAgent], functions: list[Function])\
            -> list[list[int], int]:
        solution = [0 for i in range(len(agents))]
        for i, agent in enumerate(agents):
            solution[i] = agent.di
        sum_cost = 0
        for fn in functions:
            sum_cost = sum_cost + fn.f(fn.sp.di, fn.ep.di)
        return [solution, sum_cost]

    def exec(self) -> list[list[int], int]:
        agents = self.init_agents.getAgents()
        functions = self.init_functions.getFunctions(agents)
        self.addFunctionsToAgents(agents, functions)

        DFS.getDFS(agents, functions)
        for agent in agents:
            agent.all_agents = copy.copy(agents)

        time, sum_messages = self.exec_cycle.exec(agents, functions)
        solution, sum_cost = self.getFinalSolutionAndCost(agents, functions)
        return [solution, sum_cost]