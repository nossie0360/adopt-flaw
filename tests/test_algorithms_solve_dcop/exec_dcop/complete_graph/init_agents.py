from src.module.exec.i_init_agents import IInitAgents

class InitAgents(IInitAgents):
    def __init__(self, agent_class: type) -> None:
        self._agent_class = agent_class

    def getAgents(self):
        D = list(range(3))
        n = 4
        agents = [self._agent_class(i, 0, D, disp=False) for i in range(n)]
        return agents