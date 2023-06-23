from ...i_init_functions import IInitFunctions
from ....agents.i_agent import IAgent
from ....util.function import Function

class InitFunctions(IInitFunctions):
    c_1 = 0 #10         # constant for non-zero costs
    c_2 = 0 #200        # larger constant necessary for IDB-ADOPT's counterexample in non-zero costs,
                        # used in func14 and func16 when xi==0 or xi==1 (otherwise they use c_1.)

    def func04(self, xi, xj):
        if xi == 0 and xj == 0:
            return 0 + InitFunctions.c_1
        elif xi == 0 and xj == 1:
            return 1000 + InitFunctions.c_1
        elif xi == 0 and xj == 2:
            return 1000 + InitFunctions.c_1
        elif xi == 1 and xj == 0:
            return 1000 + InitFunctions.c_1
        elif xi == 1 and xj == 1:
            return 0 + InitFunctions.c_1
        elif xi == 1 and xj == 2:
            return 1000 + InitFunctions.c_1
        elif xi == 2 and xj == 0:
            return 1000 + InitFunctions.c_1
        elif xi == 2 and xj == 1:
            return 1000 + InitFunctions.c_1
        elif xi == 2 and xj == 2:
            return 0 + InitFunctions.c_1

    def func14(self, xi, xj):
        if xi == 0 and xj == 0:
            return 5 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 0 and xj == 1:
            return 8 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 1 and xj == 0:
            return 6 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 1 and xj == 1:
            return 9 + InitFunctions.c_1 + InitFunctions.c_2
        else:
            return 1 + InitFunctions.c_1

    def func16(self, xi, xj):
        if xi == 0 and xj == 0:
            return 2 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 0 and xj == 1:
            return 2 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 1 and xj == 0:
            return 3 + InitFunctions.c_1 + InitFunctions.c_2
        elif xi == 1 and xj == 1:
            return 3 + InitFunctions.c_1 + InitFunctions.c_2
        else:
            return 1 + InitFunctions.c_1

    def getFunctions(self, agents: list[IAgent]) -> list[Function]:
        functions=[
            Function(agents[0], agents[1], lambda x,y: InitFunctions.c_1),
            Function(agents[0], agents[2], lambda x,y: InitFunctions.c_1),
            Function(agents[0], agents[4], self.func04),
            Function(agents[0], agents[6], self.func04),
            Function(agents[0], agents[8], self.func04),
            Function(agents[0], agents[10], self.func04),
            Function(agents[1], agents[3], lambda x,y: InitFunctions.c_1),
            Function(agents[3], agents[4], lambda x,y: InitFunctions.c_1),
            Function(agents[1], agents[4], self.func14),
            Function(agents[1], agents[5], lambda x,y: InitFunctions.c_1),
            Function(agents[5], agents[6], lambda x,y: InitFunctions.c_1),
            Function(agents[1], agents[6], self.func16),
            Function(agents[2], agents[7], lambda x,y: InitFunctions.c_1),
            Function(agents[7], agents[8], lambda x,y: InitFunctions.c_1),
            Function(agents[2], agents[8], self.func14),
            Function(agents[2], agents[9], lambda x,y: InitFunctions.c_1),
            Function(agents[9], agents[10], lambda x,y: InitFunctions.c_1),
            Function(agents[2], agents[10], self.func16)
        ]
        return functions