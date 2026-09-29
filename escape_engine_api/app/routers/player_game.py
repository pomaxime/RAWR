from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Player(BaseModel):
    name: str
    score: int
    level: int


players = []


@app.get("/players")
def get_players():
    return players


@app.get("/players/{player_id}")
def get_player(player_id: int):
    for player in players:
        if player["id"] == player_id:
            return player
    return "Player not found"


@app.post("/players")
def create_player(player: Player):
    new_id = max(p["id"] for p in players) + 1
    new_player = {"id": new_id, **player.model_dump()}
    players.append(new_player)
    return new_player


@app.put("/players/{player_id}")
def update_player(player_id: int, player: Player):
    for index, current_player in enumerate(players):
        if current_player["id"] == player_id:
            updated_player = {"id": player_id, **player.model_dump()}
            players[index] = updated_player
            return updated_player
    return "Player not found"


@app.delete("/players/{player_id}")
def delete_player(player_id: int):
    for index, player in enumerate(players):
        if player["id"] == player_id:
            deleted_player = players.pop(index)
            return {"message": "Player deleted", "player": deleted_player}
    return "Player not found"
