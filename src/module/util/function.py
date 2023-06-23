from __future__ import annotations
import dataclasses
from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ..agents.i_agent import IAgent

class IdCounter():
    __id = 0

    @classmethod
    def getId(cls):
        cls.__id += 1
        return cls.__id

    @classmethod
    def resetId(cls):
        cls.__id = 0

@dataclasses.dataclass(frozen=True)
class Function:
    sp: "IAgent"         # xi
    ep: "IAgent"         # xj
    f: Callable
    f_id: int = dataclasses.field(init=False)   # ID of this function. Used for ADOPT-ing

    def __post_init__(self):
        super().__setattr__("f_id", IdCounter.getId())