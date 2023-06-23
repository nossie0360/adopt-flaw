from src.module.exec.i_init_agents import IInitAgents

class InitAgents(IInitAgents):
    def __init__(self, agent_class: type) -> None:
        self._agent_class = agent_class

    def getAgents(self):
        D = [0, 1]
        agents = [
            self._agent_class(0, 0, D, disp=False),
            self._agent_class(1, 0, D, disp=False),
            self._agent_class(2, 0, D, disp=False),
            self._agent_class(3, 0, D, disp=False),
        ]
        return agents