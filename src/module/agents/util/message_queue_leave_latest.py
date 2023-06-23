from ...util.abstract_messages import Message

class MessageQueueLeaveLatest():
    def __init__(self):
        self.reached_queue : list[Message] = []
        self.unreached_queue : list[Message] = []

    def addMessage(self, msg: Message):
        self.unreached_queue.append(msg)

    def updateMessageQueue(self):
        # leave only latest messages.
        self.reached_queue = []
        for msg in reversed(self.unreached_queue):
            notAdded = True
            for added_msg in self.reached_queue:     # check overlapping
                if isinstance(msg, type(added_msg)) and msg.from_xi == added_msg.from_xi:
                    notAdded = False
                    break
            if notAdded : self.reached_queue.insert(0, msg)

        #for msg in self.message_queue[:]:
        #    if not msg.from_xi in self.pre_messages[type(msg)]:
        #        self.pre_messages[type(msg)][msg.from_xi] = copy.deepcopy(msg)
        #    elif self.pre_messages[type(msg)][msg.from_xi] == msg and type(msg) == Value:
        #        self.message_queue.remove(msg)
        #    else:
        #        self.pre_messages[type(msg)][msg.from_xi] = copy.deepcopy(msg)

        self.unreached_queue = []

    def isEmpty(self) -> bool:
        if len(self.reached_queue) == 0:
            return True
        else:
            return False

    def pop(self, index: int) -> Message:
        return self.reached_queue.pop(index)

    def getLength(self) -> int:
        return len(self.reached_queue)