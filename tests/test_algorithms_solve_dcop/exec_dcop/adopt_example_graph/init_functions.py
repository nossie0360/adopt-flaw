from src.module.exec.i_init_functions import IInitFunctions
from src.module.agents.i_agent import IAgent
from src.module.util.function import Function

class InitFunctions(IInitFunctions):
    def func(self, x, y):             # x: value of sp, y: value of ep
        if x == 0 and y == 0:
            return 2
        if x == 0 and y == 1:
            return 3
        if x == 1 and y == 0:
            return 3
        if x == 1 and y == 1:
            return 1

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        functions = [
            Function(agents[0], agents[1], self.func),
            Function(agents[0], agents[2], self.func),
            Function(agents[1], agents[2], self.func),
            Function(agents[1], agents[3], self.func),
        ]
        return functions