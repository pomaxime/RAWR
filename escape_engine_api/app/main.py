from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .domain.item import code, kaillou, key, os
from .domain.room import room_1, room_2, room_3, room_4
from .domain.time import Time

app = FastAPI(title="RAWR Escape Game")
rooms = [room_1, room_2, room_3, room_4]

progress = {
    "unlocked_index": 0,
    "completed": [],
    "keys": [],
    "ribs": 0,
    "status": "playing",
}
game_timer = Time.from_room(room_1)
inventory_items = {item.id: item for item in (key, kaillou, os, code)}


class Answer(BaseModel):
    answer: str


def refresh_game_status():
    if progress["status"] == "playing" and game_timer.remaining() <= 0:
        progress["status"] = "lost"
        game_timer.stop()
    return progress["status"]


def require_active_game():
    status = refresh_game_status()
    if status == "lost":
        raise HTTPException(
            status_code=409, detail="Partie perdue : le temps est écoulé."
        )
    if status == "won":
        raise HTTPException(status_code=409, detail="La partie est déjà terminée.")


def get_room_index(room_id: str):
    for index, room in enumerate(rooms):
        if room.id == room_id:
            return index
    return None


def can_access_room(room_id: str) -> bool:
    room_index = get_room_index(room_id)
    if room_index is None:
        return False
    room = rooms[room_index]
    return room.required_key_id is None or any(
        item["id"] == room.required_key_id for item in progress["keys"]
    )


@app.get("/")
def home():
    return {
        "message": "Bienvenue sur l'API pour mon super escape game!",
        "jeu": "/rooms",
    }


@app.get("/progress")
def get_progress():
    refresh_game_status()
    return {
        "unlocked_index": progress["unlocked_index"],
        "completed": progress["completed"],
        "keys": progress["keys"],
        "ribs": progress["ribs"],
        "status": progress["status"],
        "remaining_time": game_timer.remaining(),
        "next_room": next(
            (
                room.id
                for room in rooms
                if can_access_room(room.id) and room.id not in progress["completed"]
            ),
            None,
        ),
    }


@app.get("/rooms")
def get_rooms():
    refresh_game_status()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "locked": not can_access_room(r.id),
            "doors": [door.to_dict() for door in r.doors],
        }
        for r in rooms
    ]


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    require_active_game()
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    if not can_access_room(room_id):
        raise HTTPException(
            status_code=403,
            detail="Cette salle est verrouillée. Résolvez les salles précédentes pour débloquer la suite.",
        )
    if not game_timer.running:
        game_timer.start()
    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "puzzles": [
            {"id": p.id, "name": p.name, "description": p.description, "hints": p.hints}
            for p in room.puzzles
        ],
        "required_key_id": room.required_key_id,
        "doors": [door.to_dict() for door in room.doors],
    }


@app.post("/rooms/{room_id}/doors/{door_id}/open")
def open_room_door(room_id: str, door_id: str):
    require_active_game()
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    if not can_access_room(room_id):
        raise HTTPException(status_code=403, detail="Cette salle est verrouillée.")
    door = next((item for item in room.doors if item.id == door_id), None)
    if door is None:
        raise HTTPException(status_code=404, detail="Porte introuvable")
    inventory = [inventory_items[item["id"]] for item in progress["keys"]]
    destination = door.open_door(inventory)
    if destination is None:
        raise HTTPException(
            status_code=403, detail="Il vous manque la clé de cette porte."
        )
    if destination == "exit":
        progress["status"] = "won"
        game_timer.stop()
    return {"opened": True, "destination_room_id": destination, "door": door.to_dict()}


@app.post("/rooms/{room_id}/puzzles/{puzzle_id}/answer")
def answer_puzzle(room_id: str, puzzle_id: str, body: Answer):
    require_active_game()
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    if not can_access_room(room_id):
        raise HTTPException(
            status_code=403,
            detail="Cette salle est verrouillée. Résolvez les salles précédentes pour débloquer la suite.",
        )

    puzzle = next((p for p in room.puzzles if p.id == puzzle_id), None)
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Énigme introuvable")

    is_correct = puzzle.check_solution(body.answer)
    obtained_key = None
    if is_correct:
        room_index = get_room_index(room_id)
        if room_index is not None and room_id not in progress["completed"]:
            progress["completed"].append(room_id)
        if room.reward_key and not any(
            item["id"] == room.reward_key.id for item in progress["keys"]
        ):
            obtained_key = room.reward_key.to_dict()
            progress["keys"].append(obtained_key)
        progress["ribs"] += 1
        if room_index is not None and room_index + 1 < len(rooms):
            progress["unlocked_index"] = room_index + 1
            if can_access_room(rooms[room_index + 1].id):
                game_timer.continue_to_room(rooms[room_index + 1])
        else:
            progress["unlocked_index"] = len(rooms) - 1
        print("correct: True")
        print()

    return {"correct": is_correct, "obtained_key": obtained_key, "progress": progress}


@app.post("/veloci-ruben/ribs")
def give_ribs_to_veloci():
    require_active_game()
    if progress["ribs"] <= 0:
        raise HTTPException(
            status_code=400, detail="Vous n'avez aucun ribs disponible."
        )
    progress["ribs"] -= 1
    game_timer.add_time(600)
    return {
        "message": "Véloci Ruben a reçu un ribs.",
        "added_time": 600,
        "remaining_time": game_timer.remaining(),
        "ribs": progress["ribs"],
    }


def play_game() -> None:
    print("=== RAWR Escape Game ===")
    print(
        "Résolvez les salles dans l'ordre pour obtenir les clés et débloquer la suite."
    )
    print("Commandes : aide, quitter")

    for index, room in enumerate(rooms):
        if not can_access_room(room.id):
            print(
                f"\nLa salle {room.name} est verrouillée. Vous devez terminer la salle précédente."
            )
            break

        print(f"\n=== {room.name} ===")
        print(room.description)

        puzzle = room.puzzles[0] if room.puzzles else None
        if puzzle is None:
            print("Aucune énigme dans cette salle.")
            continue

        print(f"\nÉnigme : {puzzle.name}")
        print(puzzle.description)

        for attempt in range(1, 4):
            answer = input("Votre réponse : ").strip()
            if answer.lower() in {"quitter", "quit", "exit"}:
                print("Partie interrompue.")
                return
            if answer.lower() in {"aide", "help", "indice"}:
                if puzzle.hints:
                    print("Indices :")
                    for hint_index, hint in enumerate(puzzle.hints, start=1):
                        print(f"  {hint_index}. {hint}")
                else:
                    print("Aucun indice disponible.")
                continue

            if answer.lower() == puzzle.secret_code.lower():
                print("Bonne réponse !")
                print()
                if index + 1 < len(rooms):
                    progress["unlocked_index"] = index + 1
                else:
                    progress["unlocked_index"] = len(rooms) - 1
                if room.reward_key and not any(
                    item["id"] == room.reward_key.id for item in progress["keys"]
                ):
                    progress["keys"].append(room.reward_key.to_dict())
                print(
                    f"La clé de la salle {room.name} a été validée. La salle suivante est déverrouillée."
                )
                break

            remaining = 3 - attempt
            print(f"Mauvaise réponse. Il vous reste {remaining} tentative(s).")
            if attempt == 3:
                print("Vous n'avez plus de tentatives. Partie terminée.")
                return

    if progress["unlocked_index"] >= len(rooms) - 1:
        print(
            "\nFélicitations ! Vous avez terminé le jeu et débloqué toutes les salles."
        )


if __name__ == "__main__":
    play_game()
