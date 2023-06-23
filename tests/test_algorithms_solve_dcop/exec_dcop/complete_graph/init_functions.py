from src.module.exec.i_init_functions import IInitFunctions
from src.module.agents.i_agent import IAgent
from src.module.util.function import Function

class InitFunctions(IInitFunctions):
    def func(self, x, y):             # x: value of sp, y: value of ep
        return x + y + 1

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        n = len(agents)
        # complete graph
        functions = []
        for i in range(n):
            for j in range(i+1, n):
                functions.append(Function(agents[i], agents[j], self.func))
        return functions