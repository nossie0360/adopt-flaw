import copy

from ...i_exec_cycle import IExecCycle
from ....agents.i_agent import IAgent
from ....agents.msg_classify_agent_wrapper import MsgClassifyAgentWrapper
from ....agents.idb_adopt.idb_agent import IdbAgent
from ....util.function import Function

class ExecCycle(IExecCycle):
    def __init__(self, agent_class: IAgent = None):
        self._agent_class = agent_class
        self._root_threshold = 9999

    def exec(self, agents: list[MsgClassifyAgentWrapper], functions: list[Function]) -> list[int]:
        # process_sequence: [an agent to process,
        #                    ignored senders,
        #                    a clock time to be set for ALL agents,
        #                    an upper bound of the clock time sent messages to be processed]
        process_sequence: list[list[MsgClassifyAgentWrapper, list[MsgClassifyAgentWrapper],
                                    int, int]] = [
            [agents[1], [], 0, None],
            [agents[4], [], None, None],
            [agents[3], [], None, None],
            [agents[1], [], None, None],
            [agents[5], [], None, None],
            [agents[4], [], None, None],
            [agents[3], [], None, None],
            [agents[1], [], 100, None],
            [agents[6], [], None, None],
            [agents[5], [], None, None],
            [agents[1], [], 200, None],
            [agents[6], [], None, None],
            [agents[5], [], None, None],
            [agents[1], [], 300, None],
            [agents[0], [], None, None],
            [agents[3], [], None, 100],
            [agents[3], [], None, 200],
            [agents[3], [], None, 300],
            [agents[5], [], None, None],
            [agents[1], [], None, None],
            [agents[0], [], None, None],
            [agents[2], [], None, None],
            [agents[8], [], None, None],
            [agents[7], [], None, None],
            [agents[2], [], None, None],
            [agents[9], [], None, None],
            [agents[8], [], None, None],
            [agents[7], [], None, None],
            [agents[2], [], 400, None],
            [agents[10], [], None, None],
            [agents[9], [], None, None],
            [agents[2], [], 500, None],
            [agents[10], [], None, None],
            [agents[9], [], None, None],
            [agents[2], [], 600, None],
            [agents[0], [], None, None],
            [agents[7], [], None, 400],
            [agents[7], [], None, 500],
            [agents[7], [], None, 600],
            [agents[9], [], None, None],
            [agents[2], [], None, None],
            [agents[0], [], None, None]
        ]

        # while loop if IDB-ADOPT is run.
        idb_time = 0
        while True:
            n = len(agents)
            terminated = [False for i in range(n)]
            time = 0
            sum_messages = 0

            if self._agent_class == IdbAgent:
                idb_time = idb_time + 1
                print("\n-------------IDB: %d-------------" % idb_time)

            # initialize agents and message queue
            for agent in agents:
                agent.initializeMessageQueue()
            for agent in agents:
                if self._agent_class == IdbAgent:
                    agent.initialize_idb(self._root_threshold)
                else:
                    agent.initialize()

            while not all(terminated):
                time = time + 1
                print(".", end="")

                # update message queue except specified agents
                process_idx = (time - 1) % len(process_sequence)
                targets = [process_sequence[process_idx][0]]
                set_clock_time = process_sequence[process_idx][2]
                processed_message_time = process_sequence[process_idx][3]
                processed_sender_id = targets[0].getInvolvedAgentsId()
                processed_sender = [agent for agent in agents \
                                    if agent.xi in processed_sender_id]
                for agent in agents:
                    agent.setClock(set_clock_time)
                for ignore in process_sequence[process_idx][1]:
                    processed_sender.remove(ignore)
                for agent in targets:
                    agent.updateMessageQueueTimeConditioned(processed_message_time, processed_sender)

                if all([agent.message_queue.isEmptyForAllQueue() for agent in agents]):
                    print("--- NO MESSAGES EXIST!! ---")
                    break

                # process messages
                i = 0
                for agent in agents:
                    sum_messages = sum_messages + agent.getMessageQueueLength()
                    for target_id in agent.getInvolvedAgentsId():
                        running = True
                        while running:
                            running = agent.processMessage(target_id)
                    terminated[i] = agent.isTerminated()
                    i = i + 1

            if self._agent_class == IdbAgent:
                if agents[0].base_agent._threshold > self._root_threshold:
                    break
                else:
                    self._root_threshold = agents[0].base_agent._threshold - 1
            else:
                break

        return [time, sum_messages]