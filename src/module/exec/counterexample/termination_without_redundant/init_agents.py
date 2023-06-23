from ...i_init_agents import IInitAgents
from ....agents.msg_classify_agent_wrapper import MsgClassifyAgentWrapper

class InitAgents(IInitAgents):
    def __init__(self, agent_class: type) -> None:
        self._agent_class = agent_class

    def getAgents(self):
        __disp = False
        agents = [
            MsgClassifyAgentWrapper(self._agent_class(0, 0, [0, 1, 2], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(1, 0, [0, 1], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(2, 0, [0, 1], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(3, 0, [0], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(4, 0, [0, 1, 2], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(5, 0, [0], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(6, 0, [0, 1, 2], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(7, 0, [0], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(8, 0, [0, 1, 2], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(9, 0, [0], disp=__disp)),
            MsgClassifyAgentWrapper(self._agent_class(10, 0, [0, 1, 2], disp=__disp)),
        ]
        return agents