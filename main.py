from pokeapi.client import PokeApiClient

from models.pokemon_stats import PokemonStats

api = PokeApiClient()
pikachu = api.get_pokemon("pikachu")

charizard = api.get_pokemon("charizard")

for _ in range(10):
    pikachu.attack(charizard)
    print(charizard.hp)
    print(charizard.is_dead)