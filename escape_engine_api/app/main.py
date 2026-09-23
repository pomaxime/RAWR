from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .domain.room import room_1, room_2, room_3, room_4

app = FastAPI(title="RAWR Escape Game")
rooms = [room_1, room_2, room_3, room_4]


class Answer(BaseModel):
    answer: str


@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API pour mon super escape game!", "jeu": "/rooms"}


@app.get("/rooms")
def get_rooms():
    return [{"id": r.id, "name": r.name, "description": r.description} for r in rooms]


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = next((r for r in rooms if r.id == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Salle introuvable")
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
    puzzle = next((p for p in room.puzzles if p.id == puzzle_id), None)
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Énigme introuvable")
    return {"correct": puzzle.check_solution(body.answer)}
