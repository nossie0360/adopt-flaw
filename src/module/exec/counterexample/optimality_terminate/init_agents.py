from ...i_init_agents import IInitAgents
from ....agents.msg_classify_agent_wrapper import MsgClassifyAgentWrapper

class InitAgents(IInitAgents):
    def __init__(self, agent_class: type) -> None:
        self._agent_class = agent_class


    def getAgents(self):
        agents = [
            MsgClassifyAgentWrapper(self._agent_class(0, 0, [0, 1], disp=False)),
            MsgClassifyAgentWrapper(self._agent_class(1, 0, [0], disp=False)),
            MsgClassifyAgentWrapper(self._agent_class(2, 0, [0, 1], disp=False)),
            MsgClassifyAgentWrapper(self._agent_class(3, 0, [0, 1], disp=False)),
            MsgClassifyAgentWrapper(self._agent_class(4, 0, [0], disp=False))
        ]
        return agents