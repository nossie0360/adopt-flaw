import copy

from src.module.exec.i_exec_cycle import IExecCycle
from src.module.agents.i_agent import IAgent
from src.module.agents.msg_classify_agent_wrapper import MsgClassifyAgentWrapper
from src.module.agents.idb_adopt.idb_agent import IdbAgent
from src.module.util.function import Function

class BasicExecCycle(IExecCycle):
    def __init__(self, agent_class: IAgent = None):
        self._agent_class = agent_class
        self._root_threshold = 9999

    def exec(self, agents: list[IAgent], functions: list[Function]) -> list[int]:
        # while loop if IDB-ADOPT is run.
        idb_time = 0
        while True:
            n = len(agents)
            terminated = [False for i in range(n)]
            time = 0
            sum_messages = 0

            if self._agent_class == IdbAgent:
                idb_time = idb_time + 1
                #print("\n-------------IDB: %d-------------" % idb_time)

            # initialize agents and message queue
            for agent in agents:
                if self._agent_class == IdbAgent and agent.parent is None:
                    agent.initialize_root(self._root_threshold)
                else:
                    agent.initialize()

            while not all(terminated):
                time = time + 1
                #print(".", end="")

                # update message queue
                tmp = 0
                for agent in agents:
                    agent.updateMessageQueue()
                    tmp = tmp + agent.getMessageQueueLength()
                if tmp == 0: print("INFINITY LOOP!!!!!!!!"); break

                # process messages
                i = 0
                for agent in agents:
                    sum_messages = sum_messages + agent.getMessageQueueLength()
                    running = True
                    while running:
                        running = agent.processMessage()
                    terminated[i] = agent.isTerminated()
                    i = i + 1

            if self._agent_class == IdbAgent:
                if agents[0]._threshold > self._root_threshold:
                    break
                else:
                    self._root_threshold = agents[0]._threshold - 1
            else:
                break

        return [time, sum_messages]