from dataclasses import dataclass
from typing import List

@dataclass
class Team:
    name: str
    pokemons: List[str]