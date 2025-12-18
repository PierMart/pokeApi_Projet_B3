from dataclasses import field
from models.pokemon_stats import PokemonStats
from dataclasses import dataclass, is_dataclass, fields
from typing import List, Optional, Type, TypeVar, Any, get_type_hints, get_origin, get_args, Union
import random

T = TypeVar("T")

def from_dict(cls: Type[T], data: Any) -> T:
    if data is None:
        return None
    
    # Handle List[T]
    origin = get_origin(cls)
    if origin is list:
        arg = get_args(cls)[0]
        return [from_dict(arg, x) for x in data] # type: ignore
    
    # Handle Optional[T] which is Union[T, None]
    if origin is Union:
        args = get_args(cls)
        non_none = next((a for a in args if a is not type(None)), None)
        if non_none:
            return from_dict(non_none, data)
            
    if is_dataclass(cls):
        if not isinstance(data, dict):
            return data
            
        field_types = get_type_hints(cls)
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                kwargs[f.name] = from_dict(field_types[f.name], data[f.name])
        return cls(**kwargs)
        
    return data

@dataclass
class NamedAPIResource:
    name: str
    url: str

@dataclass
class VersionGameIndex:
    game_index: int
    version: NamedAPIResource

@dataclass
class PokemonSprites:
    front_default: Optional[str]
    front_shiny: Optional[str]
    front_female: Optional[str]
    front_shiny_female: Optional[str]
    back_default: Optional[str]
    back_shiny: Optional[str]
    back_female: Optional[str]
    back_shiny_female: Optional[str]

@dataclass
class PokemonCries:
    latest: str
    legacy: str

@dataclass
class PokemonStat:
    stat: NamedAPIResource
    effort: int
    base_stat: int

@dataclass
class PokemonMoveVersion:
    move_learn_method: NamedAPIResource
    version_group: NamedAPIResource
    level_learned_at: int
    order: int

@dataclass
class PokemonMove:
    move: NamedAPIResource
    version_group_details: List[PokemonMoveVersion]

@dataclass
class PokemonHeldItemVersion:
    version: NamedAPIResource
    rarity: int

@dataclass
class PokemonHeldItem:
    item: NamedAPIResource
    version_details: List[PokemonHeldItemVersion]

@dataclass
class PokemonAbility:
    is_hidden: bool
    slot: int
    ability: NamedAPIResource

@dataclass
class PokemonAbilityPast:
    generation: NamedAPIResource
    abilities: List[PokemonAbility]

@dataclass
class PokemonType:
    slot: int
    type: NamedAPIResource

@dataclass
class PokemonFormType:
    slot: int
    type: NamedAPIResource

@dataclass
class PokemonTypePast:
    generation: NamedAPIResource
    types: List[PokemonType]

@dataclass
class Pokemon:
    id: int
    name: str
    base_experience: int
    height: int
    is_default: bool
    order: int
    weight: int
    abilities: List[PokemonAbility]
    forms: List[NamedAPIResource]
    game_indices: List[VersionGameIndex]
    held_items: List[PokemonHeldItem]
    location_area_encounters: str
    moves: List[PokemonMove]
    past_types: List[PokemonTypePast]
    past_abilities: List[PokemonAbilityPast]
    sprites: PokemonSprites
    cries: PokemonCries
    species: NamedAPIResource
    stats: List[PokemonStat]
    types: List[PokemonType]

    _hp: int = field(init=False, repr=False)
    _is_dead: bool = field(init=False, repr=False)

    def __post_init__(self):
        hp_stat = next((s for s in self.stats if s.stat.name == "hp"), None)
        self._hp = hp_stat.base_stat if hp_stat else 0
        self._is_dead = False

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int):
        self._hp = max(0, value)  # Ne jamais descendre sous 0

    @property
    def is_dead(self) -> bool:
        return self._is_dead

    @is_dead.setter
    def is_dead(self, value: bool):
        self._is_dead = value

    @classmethod
    def from_json(cls, data: dict) -> 'Pokemon':
        return from_dict(cls, data)