from abc import ABCMeta
import dataclasses

@dataclasses.dataclass
class Message:
    from_xi: int = dataclasses.field(default=None, init=False)
    sent_clock: int = dataclasses.field(default=None, init=False)

class AbstractValue(Message, metaclass=ABCMeta):
    pass

class AbstractCost(Message, metaclass=ABCMeta):
    pass

class AbstractThreshold(Message, metaclass=ABCMeta):
    pass

class AbstractTerminate(Message, metaclass=ABCMeta):
    pass