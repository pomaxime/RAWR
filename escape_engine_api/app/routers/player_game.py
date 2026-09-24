from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Player(BaseModel):
    name: str
    score: int
    level: int


players: list[dict] = []


@app.get("/players")
def get_players():
    return players


@app.get("/players/{player_id}")
def get_player(player_id: int):
    player = next((item for item in players if item["id"] == player_id), None)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.post("/players")
def create_player(player: Player):
    next_id = max((item["id"] for item in players), default=0) + 1
    new_player = {"id": next_id, **player.model_dump()}
    players.append(new_player)
    return new_player


@app.put("/players/{player_id}")
def update_player(player_id: int, player: Player):
    for index, current_player in enumerate(players):
        if current_player["id"] == player_id:
            updated_player = {"id": player_id, **player.model_dump()}
            players[index] = updated_player
            return updated_player
    raise HTTPException(status_code=404, detail="Player not found")


@app.delete("/players/{player_id}")
def delete_player(player_id: int):
    for index, current_player in enumerate(players):
        if current_player["id"] == player_id:
            deleted_player = players.pop(index)
            return {"message": "Player deleted", "player": deleted_player}
    raise HTTPException(status_code=404, detail="Player not found")
