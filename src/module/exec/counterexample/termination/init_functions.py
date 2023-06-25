from ...i_init_functions import IInitFunctions
from ....agents.i_agent import IAgent
from ....util.function import Function

class InitFunctions(IInitFunctions):
    c = 0 # 10      # constant for non-zero costs

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        functions=[
            Function(agents[0], agents[1], lambda x,y: 0 + InitFunctions.c),
            Function(agents[0], agents[2], lambda x,y: 0 + InitFunctions.c),
            Function(agents[1], agents[3], lambda x,y: 0 + InitFunctions.c),
            Function(agents[3], agents[4], lambda x,y: 0 + InitFunctions.c),
            Function(agents[1], agents[4],
                     lambda x,y: 5 + InitFunctions.c if x==0 else 6 + InitFunctions.c),
            Function(agents[1], agents[5], lambda x,y: 0 + InitFunctions.c),
            Function(agents[5], agents[6], lambda x,y: 0 + InitFunctions.c),
            Function(agents[1], agents[6],
                     lambda x,y: 2 + InitFunctions.c if x==0 else 3 + InitFunctions.c),
            Function(agents[2], agents[7], lambda x,y: 0 + InitFunctions.c),
            Function(agents[7], agents[8], lambda x,y: 0 + InitFunctions.c),
            Function(agents[2], agents[8],
                     lambda x,y: 5 + InitFunctions.c if x==0 else 6 + InitFunctions.c),
            Function(agents[2], agents[9], lambda x,y: 0 + InitFunctions.c),
            Function(agents[9], agents[10], lambda x,y: 0 + InitFunctions.c),
            Function(agents[2], agents[10],
                     lambda x,y: 2 + InitFunctions.c if x==0 else 3 + InitFunctions.c)
        ]
        return functions