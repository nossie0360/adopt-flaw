import dataclasses

@dataclasses.dataclass(frozen=True)
class Assignment:
    xi: int     # variable id
    di: int     # value