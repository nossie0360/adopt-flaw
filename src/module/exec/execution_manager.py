import copy

from ..agents.i_agent import IAgent
from ..util.dfs import DFS
from ..util.function import Function
from .i_init_agents import IInitAgents
from .i_init_functions import IInitFunctions
from .i_exec_cycle import IExecCycle

class ExecutionManager():
    def __init__(self, init_agents: IInitAgents, init_functions: IInitFunctions,
                 exec_cycle: IExecCycle) -> None:
        self.init_agents = init_agents
        self.init_functions = init_functions
        self.exec_cycle = exec_cycle

    def displayAgentId(self, agent: IAgent):
        if isinstance(agent, IAgent):
            return agent.xi
        return None

    def displayAgentsConnection(self, agents: list[IAgent]):
        for agent in agents:
            print("======{}======".format(agent.xi))
            print("ancestors: ", [self.displayAgentId(i) for i in agent.ancestors])
            print("parent: ", self.displayAgentId(agent.parent))
            print("children: ", [self.displayAgentId(i) for i in agent.children])
            print("neighbor: ", [self.displayAgentId(i) for i in agent.neighbor])
            print("lower-neighbor: ", [self.displayAgentId(i) for i in agent.lower_neighbor])
            print("SCP: ", [self.displayAgentId(i) for i in agent.scp])
            print("all-agents: ", [self.displayAgentId(i) for i in agent.all_agents])

    def addFunctionsToAgents(self, agents: list[IAgent], functions: list[Function]):
        for f in functions:
            agents[f.sp.xi].addFuntion(f)
            agents[f.ep.xi].addFuntion(f)

    def displayFinalSolutionCost(self, agents: list[IAgent], functions: list[Function],\
        time: int, sum_messages: int):
        print("\n<< time = {}>>".format(time))
        print("----- FINISHED -----")
        print("*solutions*")
        for agent in agents:
            print("x{}: {}".format(agent.xi, agent.di))

        sum_cost = 0
        for fn in functions:
            sum_cost = sum_cost + fn.f(fn.sp.di, fn.ep.di)
        print("*global cost = {}*".format(sum_cost))
        #print("mean messages / cycle: ", sum_messages / time)

    def exec(self):
        agents = self.init_agents.getAgents()
        functions = self.init_functions.getFunctions(agents)
        self.addFunctionsToAgents(agents, functions)

        DFS.getDFS(agents, functions)
        for agent in agents:
            agent.all_agents = copy.copy(agents)
        self.displayAgentsConnection(agents)

        print("----- time = 0 -----")
        time, sum_messages = self.exec_cycle.exec(agents, functions)
        self.displayFinalSolutionCost(agents, functions, time, sum_messages)