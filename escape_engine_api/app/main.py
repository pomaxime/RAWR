from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .domain.room import room_1, room_2, room_3, room_4
from .domain.time import Time

app = FastAPI(title="RAWR Escape Game")
rooms = [room_1, room_2, room_3, room_4]

progress = {
    "unlocked_index": 0,
    "completed": [],
}
game_timer = Time.from_room(room_1)


class Answer(BaseModel):
    answer: str


def get_room_index(room_id: str):
    for index, room in enumerate(rooms):
        if room.id == room_id:
            return index
    return None


def can_access_room(room_id: str) -> bool:
    room_index = get_room_index(room_id)
    if room_index is None:
        return False
    return room_index <= progress["unlocked_index"]


@app.get("/")
def home():
    return {
        "message": "Bienvenue sur l'API pour mon super escape game!",
        "jeu": "/rooms",
    }


@app.get("/progress")
def get_progress():
    return {
        "unlocked_index": progress["unlocked_index"],
        "completed": progress["completed"],
        "remaining_time": game_timer.remaining(),
        "next_room": rooms[progress["unlocked_index"]].id
        if progress["unlocked_index"] < len(rooms)
        else None,
    }


@app.get("/rooms")
def get_rooms():
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "locked": get_room_index(r.id) is not None
            and get_room_index(r.id) > progress["unlocked_index"],
        }
        for r in rooms
    ]


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
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
    }


@app.post("/rooms/{room_id}/puzzles/{puzzle_id}/answer")
def answer_puzzle(room_id: str, puzzle_id: str, body: Answer):
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
    if is_correct:
        room_index = get_room_index(room_id)
        if room_index is not None and room_id not in progress["completed"]:
            progress["completed"].append(room_id)
        if room_index is not None and room_index + 1 < len(rooms):
            progress["unlocked_index"] = room_index + 1
            game_timer.continue_to_room(rooms[room_index + 1])
        else:
            progress["unlocked_index"] = len(rooms) - 1
        print("correct: True")
        print()

    return {"correct": is_correct, "progress": progress}


def play_game() -> None:
    print("=== RAWR Escape Game ===")
    print(
        "Résolvez les salles dans l'ordre pour obtenir les clés et débloquer la suite."
    )
    print("Commandes : aide, quitter")

    for index, room in enumerate(rooms):
        if index > progress["unlocked_index"]:
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
