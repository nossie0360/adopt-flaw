from __future__ import annotations
from typing import TYPE_CHECKING
from .message_queue import MessageQueue
from ...util.abstract_messages import Message
if TYPE_CHECKING:
    from ..i_agent import IAgent

class ClassifiedMessageQueue(MessageQueue):
    def __init__(self):
        super().__init__()
        self.reached_queue: dict[int, list[Message]] = {}
        self.unreached_queue: dict[int, list[Message]] = {}

    def initializeMessageQueue(self, neighbor: list[IAgent]):
        for a in neighbor:
            x = a.xi
            self.reached_queue[x] = []
            self.unreached_queue[x] = []

    def addMessage(self, msg: Message):
        if msg.from_xi not in self.reached_queue:
            self.reached_queue[msg.from_xi] = []
        if msg.from_xi not in self.unreached_queue:
            self.unreached_queue[msg.from_xi] = []
        self.unreached_queue[msg.from_xi].append(msg)

    def updateMessageQueue(self, neighbor: list[IAgent] = []):
        # remove messages which have same values from unreached_queue.
        # the last reached_queue is left, then unreached_queue is combined to the end of it.
        neighbor_x = [a.xi for a in neighbor]
        if len(neighbor) == 0:
            neighbor_x = self.unreached_queue.keys()
        for x in neighbor_x:
            new_queue = []
            last_messages = {}
            for msg in self.unreached_queue[x]:
                if not type(msg) in last_messages\
                    or last_messages[type(msg)] != msg:
                    new_queue.append(msg)
                    last_messages[type(msg)] = msg

            #for msg in self.unreached_queue[x]:
            #    notAdded = True
            #    for added_msg in new_queue:     # check overlapping
            #        if msg == added_msg:
            #            notAdded = False
            #            break
            #    if notAdded:
            #        new_queue.append(msg)

            #for msg in reversed(self.next_message_queue[x]):
            #    notAdded = True
            #    for added_msg in new_message_queue:     # check overlapping
            #        if isinstance(msg, type(added_msg)) and msg.from_xi == added_msg.from_xi:
            #            notAdded = False
            #            break
            #    if notAdded : new_message_queue.insert(0, msg)

            self.reached_queue[x] += new_queue
            self.unreached_queue[x] = []

    def updateMessageQueueTimeConditioned(self, targets: list[IAgent]=[],
                                          clock_time: int = None):
        """
        add messages in unreached_queue sent until clock_time to reached_queue.
        (NOT removing any messages)

        Args:
            clock_time (int): the time to add messages.
            If any number is not given, all messages are added.

        Note:
            We assume that unreached_queue is sorted in chronological order.
        """
        for a in targets:
            x = a.xi
            if clock_time is None:
                self.reached_queue[x] += self.unreached_queue[x]
                self.unreached_queue[x] = []
                continue

            while len(self.unreached_queue[x]) > 0:
                if self.unreached_queue[x][0].sent_clock > clock_time:
                    break
                msg = self.unreached_queue[x].pop(0)
                self.reached_queue[x].append(msg)

    def updateMessageQueueTypeCondition(self, targets: list[IAgent],\
         msg_type: type):
        """
        Update queue until a message whose type equals to the msg_type is found
        in the unreached queue (condition_msg is NOT ADDED).
        """
        for a in targets:
            new_queue = []
            x = a.xi
            while len(self.unreached_queue[x]) > 0:
                if isinstance(self.unreached_queue[x][0], msg_type):
                    break
                msg = self.unreached_queue[x].pop(0)
                notAdded = True
                for added_msg in new_queue:     # check overlapping
                    if msg == added_msg:
                        notAdded = False
                        break
                if notAdded:
                    new_queue.append(msg)
            self.reached_queue[x] += new_queue

    def isEmpty(self, xi: int = None):
        if xi is None:
            sum_len = sum([len(queue) for queue in self.reached_queue.values()])
            return  sum_len == 0
        else:
            return len(self.reached_queue[xi]) == 0

    def isEmptyForAllQueue(self) -> bool:
        sum_len = sum([len(queue) for queue in self.reached_queue.values()])
        sum_len += sum([len(queue) for queue in self.unreached_queue.values()])
        return sum_len == 0

    def pop(self, index: int, xi: int = None):
        if xi is None:
            for key in self.reached_queue:
                if len(self.reached_queue[key]) > 0:
                    return self.reached_queue[key].pop(index)
        else:
            return self.reached_queue[xi].pop(index)

    def getLength(self) -> int:
        ret = 0
        for key in self.reached_queue:
            ret += len(self.reached_queue[key])
        return ret

    def getQueueKeys(self) -> list[int]:
        reached_key = set(self.reached_queue.keys())
        unreached_key = set(self.unreached_queue.keys())
        union_key = reached_key.union(unreached_key)
        return list(sorted(union_key))