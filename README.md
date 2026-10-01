# RAWR

RAWR est un escape game avec une API FastAPI et un mode terminal.

## Organisation

```text
escape_engine_api/app/
├── main.py                    # création de l’application et raccordement des routers
├── cli.py                     # affichage et saisie du mode terminal
├── errors.py                  # erreurs des services, traduites en HTTP par main.py
├── models/                    # Answer, Player et objets du jeu
│   ├── answer.py
│   ├── player.py
│   ├── room.py                # Room et configuration des quatre salles
│   ├── puzzle.py
│   ├── code_puzzle.py
│   ├── hash_puzzle.py
│   ├── game_element.py
│   ├── item.py
│   ├── door.py
│   └── time.py
├── routers/
│   ├── game.py                # routes du jeu
│   └── player_game.py         # routes joueurs
└── services/
    ├── game_service.py        # progression, accès, réponses, portes et ribs
    └── player_service.py      # gestion des joueurs en mémoire
```

Les routers reçoivent les requêtes et appellent les services. Les modèles décrivent les données et les comportements des objets du jeu. Les services orchestrent les règles métier. `main.py` crée l’application, enregistre les routers et traduit les erreurs des services en réponses HTTP.

## Installation et démarrage

Depuis la racine du dépôt :

```bash
conda env create -f escape_engine_api/environment.yml
conda activate RAWR
uvicorn escape_engine_api.app.main:app --reload
```

Swagger : http://127.0.0.1:8000/docs. ReDoc : http://127.0.0.1:8000/redoc.

## Jouer

| Salle | Énigme | Réponse | Clé |
|---|---|---|---|
| room_1 | puzzle_1 | Raptor Affamé Want Ribs | key1 |
| room_2 | puzzle_2 | 32 | key2 |
| room_3 | puzzle_3 | RAPTOR | key3 |
| room_4 | puzzle_4 | BLEUE | key4 |

Les routes du jeu sont `GET /`, `GET /progress`, `GET /rooms`, `GET /rooms/{room_id}`, `POST /rooms/{room_id}/puzzles/{puzzle_id}/answer`, `POST /rooms/{room_id}/doors/{door_id}/open` et `POST /veloci-ruben/ribs`.

Une réponse correcte donne une clé et un ribs. La clé débloque la salle suivante et ouvre sa porte. Donner un ribs à Véloci Ruben ajoute 600 secondes au temps restant. Le chronomètre commence à la première consultation d’une salle et conserve le temps restant entre les salles. Ouvrir `door_4` dans `room_4` termine la partie avec le statut `won`. Le statut passe à `lost` quand le temps est écoulé; les actions de jeu renvoient alors HTTP 409.

Exemple de réponse :

```bash
curl -X POST http://127.0.0.1:8000/rooms/room_1/puzzles/puzzle_1/answer \
  -H 'Content-Type: application/json' \
  -d '{"answer":"Raptor Affamé Want Ribs"}'
```

Les réponses API sont sensibles à la casse. Une salle inconnue renvoie 404, une salle verrouillée 403, et un champ `answer` manquant 422.

Le mode terminal reste disponible :

```bash
python -m escape_engine_api.app.main
# ou
python -m escape_engine_api.app.cli
```

Il accepte `aide`/`help`/`indice` et `quitter`/`quit`/`exit`, jusqu’à trois tentatives par énigme, et compare les réponses sans tenir compte de la casse.

## Joueurs

Les routes `GET /players`, `GET /players/{player_id}`, `POST /players`, `PUT /players/{player_id}` et `DELETE /players/{player_id}` sont raccordées à l’application. Le modèle exige `name`, `score` et `level`. Un joueur inconnu renvoie 404.

## Vérification

Démarrer un serveur neuf puis lancer :

```bash
bash test.sh
# Avec un autre port :
BASE_URL=http://127.0.0.1:8001 bash test.sh
```

Le script vérifie les erreurs, les salles verrouillées, les quatre énigmes, les portes, les ribs, la victoire et la documentation FastAPI. Il modifie la progression : redémarrer le serveur avant chaque exécution.

La progression et les joueurs restent globaux au processus et en mémoire : ils sont partagés entre les clients et réinitialisés au redémarrage.
