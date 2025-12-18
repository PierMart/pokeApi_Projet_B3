from dataclasses import dataclass
from models.pokemon import from_dict

@dataclass
class PokemonsResponse:
    name: str
    url: str

    @classmethod
    def from_json(cls, data: dict) -> 'PokemonsResponse':
        return from_dict(cls, data)