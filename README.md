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

Ou utilisez le fichier requirements.txt :

```bash
pip install -r requirements.txt
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
├── pokeapi/               # Client API
│   └── client.py          # Client pour interagir avec l'API PokéAPI
└── pokedex/               # Application Django
    ├── manage.py          # Script de gestion Django
    └── pokemon/           # Application Django pour les Pokémon
        ├── urls.py        # Routes de l'application
        ├── views.py       # Vues de l'application
        └── templates/     # Templates HTML
```

## Lancement de l'application

Pour lancer le serveur Django :

```bash
cd pokedex
python manage.py runserver
```

L'application sera accessible à l'adresse : `http://127.0.0.1:8000/`

## URLs disponibles

### Liste des Pokémon (Pokedex)
- **URL** : `/` ou `/pokemon/`
- **Nom de route** : `pokemon:list`
- **Description** : Affiche la liste paginée des 251 premiers Pokémon (20 par page)

### Détails d'un Pokémon
- **URL** : `/pokemon/<pokemon_id>/`
- **Nom de route** : `pokemon:detail`
- **Description** : Affiche les détails complets d'un Pokémon spécifique
- **Exemple** : `/pokemon/25/` pour voir Pikachu

### Page de combat (Sélection des équipes)
- **URL** : `/battle/`
- **Nom de route** : `pokemon:battle`
- **Description** : Génère deux équipes de 6 Pokémon aléatoires (Équipe Rouge vs Équipe Bleue) et affiche la page de préparation au combat


## Fonctionnalités

- **Consultation du Pokedex** : Visualisation des 251 premiers Pokémon avec pagination
- **Gestion d'équipes** : Génération automatique d'équipes de 6 Pokémon avec leurs statistiques
- **Système de combat** : Combat entre deux équipes avec calcul des dégâts basé sur les stats d'attaque et de défense

## Système de combat

### Comment jouer

1. **Accéder au combat** : Rendez-vous sur `/battle/` pour générer deux équipes aléatoires de 6 Pokémon chacune
2. **Attaquer** : 
   - Utilisez le bouton d'attaque de l'Équipe Rouge pour faire attaquer votre premier Pokémon
   - L'Équipe Bleue peut également attaquer
   - Les attaques alternent entre les deux équipes
3. **Gestion des Pokémon** : 
   - Quand un Pokémon tombe à 0 HP, il est automatiquement remplacé par le suivant dans l'équipe
   - Le combat continue jusqu'à ce qu'une équipe n'ait plus de Pokémon valides
4. **Victoire** : L'équipe qui élimine tous les Pokémon adverses remporte le combat

### Calcul des dégâts

On récupère via l'api les stats des pokemons, puis on calcul quelques valeurs 

**Fonctionnement :**
1. On récupère la valeur de **défense** du Pokémon attaqué depuis ses statistiques
2. On récupère la valeur d'**attaque** du Pokémon attaquant depuis ses statistiques (Il y a 10% de chance qu'un pokemon fasse un coup critique)
3. Les dégâts sont calculés selon la formule : `attaque × (défense / 255)`
4. Les points de vie (HP) du Pokémon attaqué sont réduits de ce montant
5. Si les HP tombent à 0 ou moins, le Pokémon est marqué comme mort (`is_dead = True`)

Pour réinitialiser un combat, utilisez l'action `reset` ou rechargez la page `/battle/`.
