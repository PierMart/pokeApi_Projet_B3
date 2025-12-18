from pokeapi.client import PokeApiClient

api = PokeApiClient()
pikachu = api.get_pokemon("pikachu")
