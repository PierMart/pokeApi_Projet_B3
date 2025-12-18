TARTRAU Thomas
FAUVELLE Fiona
MARTINEZ Pierre
LEVENEZ Alexandre

# Documentation

## Vue d'ensemble

Ce projet est un pokedex où l'on peut voir les 251 premiers pokemons. 
En plus de voir tout ces pokemons, on peut faire des équipes de 6 pokemons avec chacun des stats différents.
Un système de combat a été mis en place qui permet de pouvoir faire des combats contre une machine.

## Récupération du projet

Pour récupérer le projet depuis Git, utilisez la commande suivante :

```bash
git clone <URL_DU_REPO>
cd pokeApi_Projet_B3
```

## Installation

Pensez à bien installer les dépendances !

```bash
pip install django
pip install requests
```

## Structure du projet

```
pokeApi_Projet_B3/
├── main.py                 # Point d'entrée de l'application
├── models/                 # Modèles de données
│   ├── pokemon.py         # Modèle principal pour les Pokémon avec système de combat
│   ├── pokemon_stats.py   # Modèle pour les statistiques des Pokémon
│   ├── pokemons_response.py  # Modèle pour les réponses de liste de Pokémon
│   └── team.py            # Modèle pour représenter une équipe de Pokémon
└── pokeapi/               # Client API
    └── client.py          # Client pour interagir avec l'API PokéAPI
```

## Fonctionnalités

- **Consultation du Pokedex** : Visualisation des 251 premiers Pokémon
- **Gestion d'équipes** : Création d'équipes de 6 Pokémon avec leurs statistiques
- **Système de combat** : Combat entre Pokémon avec calcul des dégâts basé sur les stats d'attaque et de défense

### Système de combat

**Fonctionnement :**
1. On récupère la valeur de **défense** du Pokémon attaqué depuis ses statistiques
2. On récupère la valeur d'**attaque** du Pokémon attaquant depuis ses statistiques
3. Les dégâts sont calculés selon la formule : `attaque × (défense / 255)`
4. Les points de vie (HP) du Pokémon attaqué sont réduits de ce montant
5. Si les HP tombent à 0 ou moins, le Pokémon est marqué comme mort (`is_dead = True`)