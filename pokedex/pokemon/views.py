from django.shortcuts import render
from django.http import HttpRequest
from pokeapi.client import PokeApiClient
import random
api = PokeApiClient()


MAX_POKEMON = 251  # Limiter aux 251 premiers (Gen 1 & 2)

def pokedex_list(request: HttpRequest):
    """Display list of all Pokemon"""
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
    """Display details of a specific Pokemon"""
    pokemon = api.get_pokemon(pokemon_id)
    
    context = {
        'pokemon': pokemon,
    }
    return render(request, 'pokemon/detail.html', context)

def pokemon_to_cache(pokemon):
    """Convertit un Pokemon en dict pour le cache session"""
    return {
        'id': pokemon.id,
        'name': pokemon.name,
        'hp': pokemon.hp,
        'sprites_front': pokemon.sprites.front_default,
        'sprites_back': pokemon.sprites.back_default,
        'stats': [{'name': s.stat.name, 'base_stat': s.base_stat} for s in pokemon.stats],
    }

def battle_view(request: HttpRequest):
    """Display battle view"""
    # Clear toutes les données de combat précédent
    for key in ['team1_hp', 'team2_hp', 'current_pokemon1', 'current_pokemon2', 'battle_log', 'team1_cache', 'team2_cache']:
        request.session.pop(key, None)
    
    all_ids = random.sample(range(1, 252), 12) 
    team1_pokemons = []
    team2_pokemons = []
    team1_cache = []
    team2_cache = []
    
    #Charger 6 Pokemon aléatoirement pour chaque équipe et les mettre en cache
    for pid in all_ids[:6]:
        pokemon = api.get_pokemon(pid)
        team1_pokemons.append(pokemon)
        team1_cache.append(pokemon_to_cache(pokemon))

    for pid in all_ids[6:]:
        pokemon = api.get_pokemon(pid)
        team2_pokemons.append(pokemon)
        team2_cache.append(pokemon_to_cache(pokemon))
    
    # Stocker le cache des Pokémon en session
    request.session['team1_cache'] = team1_cache
    request.session['team2_cache'] = team2_cache
    
    context = {
        'team1':{'name': 'Equipe Rouge', 'pokemons': team1_pokemons},
        'team2':{'name': 'Equipe Bleue', 'pokemons': team2_pokemons},
    }
    return render(request, 'pokemon/battle.html', context)

class CachedPokemon:
    """Pokemon léger reconstruit depuis le cache (sans appel API)"""
    def __init__(self, data, current_hp=None):
        self.id = data['id']
        self.name = data['name']
        self.max_hp = data['hp']
        self._hp = current_hp if current_hp is not None else data['hp']
        self._is_dead = self._hp <= 0
        self.sprites_front = data['sprites_front']
        self.sprites_back = data['sprites_back']
        self.stats = data['stats']
    
    @property
    def hp(self):
        return self._hp
    
    @hp.setter
    def hp(self, value):
        self._hp = max(0, value)
    
    @property
    def is_dead(self):
        return self._is_dead
    
    @is_dead.setter
    def is_dead(self, value):
        self._is_dead = value
    
    def get_stat(self, name):
        return next((s['base_stat'] for s in self.stats if s['name'] == name), 0)
    
    def attack(self, defender):
        if defender.is_dead:
            return 0, False
        attack_val = self.get_stat('attack')
        defense_val = defender.get_stat('defense')
        damage = attack_val * (defense_val / 255)
        
        is_critical = random.random() < 0.10
        if is_critical:
            damage *= 2
        
        defender.hp -= damage
        if defender.hp <= 0:
            defender.is_dead = True
        return damage, is_critical

def fight_view(request: HttpRequest):
    """Interactive battle view"""
    from django.shortcuts import redirect
    
    # Si c'est un GET direct (refresh ou accès direct), rediriger vers battle pour nouvelles équipes
    if request.method == 'GET' and 'team1_hp' in request.session:
        # Si combat déjà en cours mais refresh = reset tout
        for key in ['team1_hp', 'team2_hp', 'current_pokemon1', 'current_pokemon2', 'battle_log', 'team1_cache', 'team2_cache']:
            request.session.pop(key, None)
        return redirect('pokemon:battle')
    
    # Récupérer le cache des équipes
    team1_cache = request.session.get('team1_cache', [])
    team2_cache = request.session.get('team2_cache', [])
    
    if not team1_cache or not team2_cache:
        return redirect('pokemon:battle')
    
    # Initialiser les HP en session si pas déjà fait
    if 'team1_hp' not in request.session:
        request.session['team1_hp'] = [p['hp'] for p in team1_cache]
        request.session['team2_hp'] = [p['hp'] for p in team2_cache]
        request.session['current_pokemon1'] = 0
        request.session['current_pokemon2'] = 0
        request.session['battle_log'] = []
    
    # Reconstruire les Pokémon depuis le cache (SANS appel API)
    team1 = [CachedPokemon(data, request.session['team1_hp'][i]) for i, data in enumerate(team1_cache)]
    team2 = [CachedPokemon(data, request.session['team2_hp'][i]) for i, data in enumerate(team2_cache)]
    
    current1 = request.session['current_pokemon1']
    current2 = request.session['current_pokemon2']
    battle_log = request.session['battle_log']
    winner = None
    
    # Gérer les attaques
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'attack1' and current1 < 6 and current2 < 6:
            # Équipe 1 attaque
            attacker = team1[current1]
            defender = team2[current2]
            if not attacker.is_dead and not defender.is_dead:
                old_hp = defender.hp
                damage, is_critical = attacker.attack(defender)
                damage = round(old_hp - defender.hp, 1)
                if is_critical:
                    battle_log.append(f"💥 COUP CRITIQUE ! {attacker.name} inflige {damage} dégâts à {defender.name}!")
                else:
                    battle_log.append(f"{attacker.name} inflige {damage} dégâts à {defender.name}!")
                request.session['team2_hp'][current2] = defender.hp
                if defender.is_dead:
                    battle_log.append(f"{defender.name} est K.O.!")
                    request.session['current_pokemon2'] = current2 + 1
        
        elif action == 'attack2' and current1 < 6 and current2 < 6:
            # Équipe 2 attaque
            attacker = team2[current2]
            defender = team1[current1]
            if not attacker.is_dead and not defender.is_dead:
                old_hp = defender.hp
                damage, is_critical = attacker.attack(defender)
                damage = round(old_hp - defender.hp, 1)
                if is_critical:
                    battle_log.append(f"💥 COUP CRITIQUE ! {attacker.name} inflige {damage} dégâts à {defender.name}!")
                else:
                    battle_log.append(f"{attacker.name} inflige {damage} dégâts à {defender.name}!")
                request.session['team1_hp'][current1] = defender.hp
                if defender.is_dead:
                    battle_log.append(f"{defender.name} est K.O.!")
                    request.session['current_pokemon1'] = current1 + 1
        
        elif action == 'reset':
            for key in ['team1_hp', 'team2_hp', 'current_pokemon1', 'current_pokemon2', 'battle_log']:
                request.session.pop(key, None)
            return redirect('pokemon:battle')
        
        request.session['battle_log'] = battle_log
        request.session.modified = True
        
        # Recharger les indices
        current1 = request.session['current_pokemon1']
        current2 = request.session['current_pokemon2']
    
    # Vérifier le gagnant
    if current1 >= 6:
        winner = "Équipe Bleue"
    elif current2 >= 6:
        winner = "Équipe Rouge"
    
    # Préparer les données des équipes avec statut
    team1_data = []
    for i, p in enumerate(team1):
        team1_data.append({
            'pokemon': p,
            'hp': request.session['team1_hp'][i],
            'max_hp': p.max_hp,
            'is_current': i == min(current1, 5),
            'is_dead': request.session['team1_hp'][i] <= 0,
        })
    
    team2_data = []
    for i, p in enumerate(team2):
        team2_data.append({
            'pokemon': p,
            'hp': request.session['team2_hp'][i],
            'max_hp': p.max_hp,
            'is_current': i == min(current2, 5),
            'is_dead': request.session['team2_hp'][i] <= 0,
        })
    
    # Pokémon actuels pour l'affichage principal
    current_pokemon1 = team1[min(current1, 5)]
    current_pokemon2 = team2[min(current2, 5)]
    current_hp1 = request.session['team1_hp'][min(current1, 5)]
    current_hp2 = request.session['team2_hp'][min(current2, 5)]
    max_hp1 = current_pokemon1.max_hp
    max_hp2 = current_pokemon2.max_hp
    
    context = {
        'team1': team1,
        'team2': team2,
        'team1_data': team1_data,
        'team2_data': team2_data,
        'current1': min(current1, 5),
        'current2': min(current2, 5),
        'current_pokemon1': current_pokemon1,
        'current_pokemon2': current_pokemon2,
        'current_hp1': current_hp1,
        'current_hp2': current_hp2,
        'max_hp1': max_hp1,
        'max_hp2': max_hp2,
        'hp_percent1': max(0, (current_hp1 / max_hp1) * 100) if max_hp1 > 0 else 0,
        'hp_percent2': max(0, (current_hp2 / max_hp2) * 100) if max_hp2 > 0 else 0,
        'battle_log': battle_log[-10:],
        'winner': winner,
    }
    return render(request, 'pokemon/fight.html', context)
    