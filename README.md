# RAWR

RAWR est un petit projet Python autour d'un escape game. Le dépôt contient une API FastAPI jouable par étapes, un mode de jeu dans le terminal, des classes métier (salles, énigmes, objets, portes et temps) et un routeur expérimental de gestion de joueurs.

> L'application effectivement démarrée par Uvicorn est `escape_engine_api.app.main:app`. Le routeur `app/routers/player_game.py` est indépendant et n'est pas branché à cette application : les routes `/players` ne sont donc pas disponibles sur le serveur actuel.

## Arborescence

```text
escape_engine_api/
├── environment.yml             # environnement Conda et dépendances déclarées
├── explication_class.txt        # résumé des classes métier
└── app/
    ├── main.py                  # application FastAPI, routes du jeu et mode terminal
    ├── domain/
    │   ├── room.py               # Room et données des quatre salles/énigmes
    │   ├── puzzle.py             # classe de base Puzzle
    │   ├── code_puzzle.py        # vérification d'un code en clair
    │   ├── hash_puzzle.py        # vérification SHA-256
    │   ├── game_element.py       # classe de base des éléments
    │   ├── item.py               # Item, Key, Ribs
    │   ├── door.py               # Door
    │   └── time.py               # chronomètre
    └── routers/
        └── player_game.py        # API joueurs isolée, non montée
```

## Ce que fait le jeu actuellement

L'API maintient une progression globale en mémoire. Au démarrage, `room_1` est accessible sans clé et les salles suivantes sont verrouillées. Résoudre l'énigme d'une salle donne sa clé, qui est ajoutée à l'inventaire et permet d'accéder à la salle suivante. La progression n'est ni enregistrée sur disque ni séparée par joueur : elle repart de zéro à chaque redémarrage du processus, et tous les clients d'un même processus partagent la même progression.

Les quatre salles, leurs codes et leurs clés sont :

| Identifiant | Salle | Réponse attendue | Clé obtenue | Ouvre |
|---|---|---|---|---|
| `room_1` | Le laboratoire de Véloci Ruben | `Raptor Affamé Want Ribs` | `key1` — Key | `room_2` |
| `room_2` | La salle des ordinateurs | `32` | `key2` — Kaillou | `room_3` |
| `room_3` | La salle de cryptographie | `RAPTOR` | `key3` — Os | `room_4` |
| `room_4` | La salle des cages | `BLEUE` | `key4` — Code | La sortie (à implémenter) |

La réponse à une énigme renvoie la clé nouvellement gagnée dans `obtained_key`. La route `GET /progress` renvoie les clés détenues dans `keys`. Les salles suivantes vérifient l'identifiant de clé requis avant d'autoriser l'accès.

Les réponses par l'API sont comparées exactement (majuscules/minuscules et accents compris). Le mode terminal, lui, compare sans tenir compte de la casse. Les indices sont renvoyés avec les détails de la salle, mais il n'existe pas de route dédiée pour demander un indice.

Le domaine contient également `HashPuzzle`, qui compare le SHA-256 de la réponse à un hash attendu, ainsi que des classes `Item`, `Key`, `Ribs`, `Door` et `Time`. Ces composants ne sont pas encore utilisés par les routes du jeu. `room.py` donne à chaque salle une limite de 900 secondes, mais le chronomètre n'est pas appliqué par l'API.

## Installation et démarrage

Depuis la racine du dépôt :

```bash
conda env create -f escape_engine_api/environment.yml
conda activate RAWR
```

Le fichier déclare Python 3.11 ou plus et FastAPI/Uvicorn, entre autres. Pour lancer l'API en mode développement :

```bash
uvicorn escape_engine_api.app.main:app --reload
```

Si le paquet n'est pas importable depuis la racine dans votre configuration, placez-vous dans `escape_engine_api/`, puis lancez `uvicorn app.main:app --reload`.

Par défaut, Uvicorn écoute sur `http://127.0.0.1:8000`. L'interface interactive Swagger est disponible sur [`/docs`](http://127.0.0.1:8000/docs), la documentation ReDoc sur [`/redoc`](http://127.0.0.1:8000/redoc), et le schéma OpenAPI sur [`/openapi.json`](http://127.0.0.1:8000/openapi.json).

## Routes de l'API active

Toutes les routes ci-dessous appartiennent à `escape_engine_api.app.main:app`.

| Méthode | Chemin | Fonction |
|---|---|---|
| `GET` | `/` | Message d'accueil et lien vers `/rooms` |
| `GET` | `/progress` | Index, salles terminées, clés détenues, temps restant et prochaine salle accessible |
| `GET` | `/rooms` | Liste des salles, descriptions et état verrouillé |
| `GET` | `/rooms/{room_id}` | Détail d'une salle accessible et de ses énigmes/indices |
| `POST` | `/rooms/{room_id}/puzzles/{puzzle_id}/answer` | Soumet une réponse et renvoie le résultat/la progression |
| `GET` | `/docs`, `/redoc`, `/openapi.json` | Documentation et schéma générés par FastAPI |

Les identifiants valides sont `room_1` à `room_4` et `puzzle_1` à `puzzle_4`, en correspondance. Une salle inconnue renvoie `404`; une salle existante mais verrouillée renvoie `403`. Une réponse manquante ou mal formée est rejetée par Pydantic avec `422`.

### Exemple de parcours avec curl

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/progress
curl http://127.0.0.1:8000/rooms
curl http://127.0.0.1:8000/rooms/room_1

curl -X POST http://127.0.0.1:8000/rooms/room_1/puzzles/puzzle_1/answer \
  -H 'Content-Type: application/json' \
  -d '{"answer":"Raptor Affamé Want Ribs"}'
```

Après une réponse correcte, consulter `/progress`, puis récupérer la salle suivante. Répéter avec les codes indiqués dans le tableau.

### Mode terminal

Le même module propose un jeu en ligne de commande :

```bash
python -m escape_engine_api.app.main
```

Il affiche les salles dans l'ordre, autorise jusqu'à trois mauvaises tentatives par énigme et accepte `aide`/`help`/`indice` pour afficher les indices ainsi que `quitter`/`quit`/`exit` pour interrompre la partie. Ce mode partage les données de progression du module pendant son processus.

## Routeur joueurs présent dans le dépôt mais non actif

`escape_engine_api/app/routers/player_game.py` définit une autre application FastAPI autonome et une liste `players` en mémoire, initialement vide. Il contient `GET /players`, `GET /players/{player_id}`, `POST /players`, `PUT /players/{player_id}` et `DELETE /players/{player_id}`. Aucun de ces chemins n'est enregistré dans `main.py`, donc appeler `/players` sur le serveur décrit plus haut renvoie actuellement `404`.

Ce routeur n'est pas prêt à servir tel quel : la création calcule le prochain identifiant avec `max(...)` sur une liste vide, ce qui provoque une erreur; le modèle `Player` exige `name`, `score` et `level`, et les réponses « Player not found » sont actuellement des chaînes plutôt que des erreurs HTTP `404`. Il faudrait le convertir en `APIRouter`, le monter dans `main.py` puis corriger ces cas avant de le proposer comme API fonctionnelle.

## Tests HTTP des routes

Lancer d'abord le serveur avec Uvicorn, puis dans un autre terminal à la racine du dépôt :

```bash
chmod +x test.sh
./test.sh
```

Le script utilise `curl` et vérifie les codes HTTP des routes actives, les erreurs attendues, les réponses invalides et un parcours complet des quatre salles. Pour que le contrôle du verrouillage initial soit déterministe, redémarrer le serveur juste avant le script. L'adresse peut être changée ainsi :

```bash
BASE_URL=http://127.0.0.1:8001 ./test.sh
```

Le test modifie la progression en mémoire du serveur en résolvant les énigmes. Redémarrer Uvicorn restaure l'état initial.

## Limites connues du code actuel

- La progression et les clés sont globales au processus, volatiles, sans utilisateur ni persistance.
- La dernière salle peut être soumise à nouveau; il n'y a pas de notion de partie terminée côté API.
- Une soumission correcte débloque l'index suivant, mais il n'existe ni inventaire ni contrôle de portes/objets.
- Les classes de temps et d'objets ne sont pas reliées aux routes.
- Les réponses API sont sensibles à la casse, contrairement au mode terminal.
- Le routeur joueurs est isolé et contient les problèmes décrits ci-dessus.
