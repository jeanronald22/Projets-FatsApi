from dataclasses import dataclass
from typing import Union

@dataclass
class Pokemon():
    id: int
    name:str
    types:list[str]
    total :int
    hp:int
    attack:int
    defense: int
    attack_special:int
    defense_special:int
    speed:int
    evolution_id: Union[int, None] = None
