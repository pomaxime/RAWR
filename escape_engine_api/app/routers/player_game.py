from fastapi import APIRouter
from ..models.player import Player
from ..services.player_service import player_service

router = APIRouter()

@router.get('/players')
def get_players():
    return player_service.get_players()

@router.get('/players/{player_id}')
def get_player(player_id: int):
    return player_service.get_player(player_id)

@router.post('/players')
def create_player(player: Player):
    return player_service.create_player(player)

@router.put('/players/{player_id}')
def update_player(player_id: int, player: Player):
    return player_service.update_player(player_id, player)

@router.delete('/players/{player_id}')
def delete_player(player_id: int):
    return player_service.delete_player(player_id)
