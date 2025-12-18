from dataclasses import dataclass

@dataclass
class PokemonStats:
    name: str
    base_stat: int

    @classmethod
    def from_api_list(cls, stats_list: list) -> list["PokemonStats"]:
        return [
            cls(name=stat.stat.name, base_stat=stat.base_stat)
            for stat in stats_list
        ]
    