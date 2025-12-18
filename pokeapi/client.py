from models.pokemons_response import PokemonsResponse
import requests

from models.pokemon import Pokemon

class PokeApiClient:
    def __init__(self):
        self.baseUrl = "https://pokeapi.co/api/v2/"

    def get_pokemon(self, pokemon: str | int) -> Pokemon:
        response = requests.get(f"{self.baseUrl}pokemon/{pokemon}")
        return Pokemon.from_json(response.json())

    def get_alls(self, limit: int = 20, offset: int = 0) -> list[Pokemon]:
        response = requests.get(f"{self.baseUrl}pokemon?limit={limit}&offset={offset}")
        return [PokemonsResponse.from_json(pokemon) for pokemon in response.json()["results"]]
