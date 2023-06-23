from ...i_init_functions import IInitFunctions
from ....agents.i_agent import IAgent
from ....util.function import Function

class InitFunctions(IInitFunctions):
    c = 0 # 10      # constant for non-zero costs

    def func(self, x, y):             # x: value of sp, y: value of ep
        return x + y + InitFunctions.c

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        n = len(agents)
        # complete graph
        functions = [
            Function(agents[0], agents[1], lambda x,y: InitFunctions.c),
            Function(agents[1], agents[2], lambda x,y: InitFunctions.c),
            Function(agents[0], agents[2],
                     lambda x,y: InitFunctions.c if x==1 and y==1 else 100 + InitFunctions.c),
        ]

        return functions