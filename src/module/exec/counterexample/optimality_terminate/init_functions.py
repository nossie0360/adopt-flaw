from ...i_init_functions import IInitFunctions
from ....agents.i_agent import IAgent
from ....util.function import Function

class InitFunctions(IInitFunctions):
    c = 0 # 10      # constant for non-zero costs

    def func03(self, x, y):             # x: value of sp, y: value of ep
        if x == 0 and y == 0:
            return 1 + InitFunctions.c
        elif x == 0 and y == 1:
            return 1000 + InitFunctions.c
        elif x == 1 and y == 0:
            return 1000 + InitFunctions.c
        elif x == 1 and y == 1:
            return 100 + InitFunctions.c

    def func23(self, x, y):             # x: value of sp, y: value of ep
        if x == 0 and y == 0:
            return 0 + InitFunctions.c
        elif x == 0 and y == 1:
            return 100 + InitFunctions.c
        elif x == 1 and y == 0:
            return 10 + InitFunctions.c
        elif x == 1 and y == 1:
            return 0 + InitFunctions.c

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        n = len(agents)
        # straight graph
        functions = [
            Function(agents[0], agents[1], lambda x,y: 0 + InitFunctions.c),
            Function(agents[1], agents[2], lambda x,y: 0 + InitFunctions.c),
            Function(agents[2], agents[3], self.func23),
            Function(agents[0], agents[4],
                     lambda x,y: 0 + InitFunctions.c if x == 0 else 1000 + InitFunctions.c),
            Function(agents[0], agents[3], self.func03)
        ]
        return functions