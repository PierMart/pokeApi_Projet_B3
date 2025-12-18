from django.shortcuts import render
from django.http import HttpRequest
from pokeapi.client import PokeApiClient

api = PokeApiClient()


MAX_POKEMON = 251  # Limiter aux 251 premiers (Gen 1 & 2)

def index(request: HttpRequest):
    """Page d'accueil du Pokédex"""
    return render(request, 'pokemon/index.html')

def pokedex_list(request: HttpRequest):
    """Afficher la liste de tous les Pokémon"""
    page = int(request.GET.get('page', 1))
    limit = 20
    offset = (page - 1) * limit
    
    # Ne pas dépasser les 251 premiers Pokémon
    if offset >= MAX_POKEMON:
        offset = MAX_POKEMON - limit
        page = (offset // limit) + 1
    
    # Ajuster la limite si on approche de la fin
    remaining = MAX_POKEMON - offset
    actual_limit = min(limit, remaining)
    
    pokemons_data = api.get_alls(limit=actual_limit, offset=offset)
    
    # Extract Pokemon ID from URL and create enriched list
    pokemons = []
    for p in pokemons_data:
        pokemon_id = p.url.rstrip('/').split('/')[-1]
        pokemons.append({
            'name': p.name,
            'id': pokemon_id,
            'url': p.url,
        })
    
    # Calculer s'il y a une page suivante
    has_next = (offset + actual_limit) < MAX_POKEMON
    
    context = {
        'pokemons': pokemons,
        'current_page': page,
        'next_page': page + 1 if has_next else None,
        'prev_page': page - 1 if page > 1 else None,
        'total_pokemon': MAX_POKEMON,
    }
    return render(request, 'pokemon/list.html', context)


def pokemon_detail(request: HttpRequest, pokemon_id: str):
    """Afficher les détails d'un Pokémon spécifique"""
    pokemon = api.get_pokemon(pokemon_id)
    
    context = {
        'pokemon': pokemon,
    }
    return render(request, 'pokemon/detail.html', context)
