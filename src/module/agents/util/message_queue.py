from ...util.abstract_messages import Message

class MessageQueue():
    def __init__(self):
        self.reached_queue : list[Message] = []
        self.unreached_queue : list[Message] = []

    def addMessage(self, msg: Message):
        self.unreached_queue.append(msg)

    def updateMessageQueue(self):
        """
        remove messages which have same values from unreached_queue.
        the last reached_queue is left, then unreached_queue is combined to the end of it.
        """
        new_queue = []
        for msg in self.unreached_queue:
            notAdded = True
            for added_msg in new_queue:     # check overlapping
                if msg == added_msg:
                    notAdded = False
                    break
            if notAdded:
                new_queue.append(msg)
        #for msg in reversed(self.next_message_queue[x]):
        #    notAdded = True
        #    for added_msg in new_message_queue:     # check overlapping
        #        if isinstance(msg, type(added_msg)) and msg.from_xi == added_msg.from_xi:
        #            notAdded = False
        #            break
        #    if notAdded : new_message_queue.insert(0, msg)
        self.reached_queue += new_queue
        self.unreached_queue = []

    def updateMessageQueueTimeConditioned(self, clock_time: int = None):
        """
        add messages in unreached_queue sent until clock_time to reached_queue.
        (NOT removing any messages)

        Args:
            clock_time (int): the time to add messages.
            If any number is not given, all messages are added.

        Note:
            We assume that unreached_queue is sorted in chronological order.
        """
        if clock_time is None:
            self.reached_queue += self.unreached_queue
            self.unreached_queue = []
            return

        while len(self.unreached_queue) > 0:
            if self.unreached_queue[0].sent_clock > clock_time:
                return
            msg = self.unreached_queue.pop(0)
            self.reached_queue.append(msg)

    def isEmpty(self) -> bool:
        if len(self.reached_queue) == 0:
            return True
        else:
            return False

    def isEmptyForAllQueue(self) -> bool:
        return len(self.reached_queue) == 0 and len(self.unreached_queue) == 0

    def pop(self, index: int) -> Message:
        return self.reached_queue.pop(index)

    def getLength(self) -> int:
        return len(self.reached_queue)