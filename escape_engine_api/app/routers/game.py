from fastapi import APIRouter
from ..models.answer import Answer
from ..services.game_service import game_service

router = APIRouter()

@router.get('/')
def home():
    return {'message': "Bienvenue sur l'API de notre Escape Game 'RAWR' !", 'jeu': '/rooms'}

@router.get('/progress')
def get_progress():
    return game_service.get_progress()

@router.get('/rooms')
def get_rooms():
    return game_service.get_rooms()

@router.get('/rooms/{room_id}')
def get_room(room_id: str):
    return game_service.get_room(room_id)

@router.post('/rooms/{room_id}/doors/{door_id}/open')
def open_room_door(room_id: str, door_id: str):
    return game_service.open_room_door(room_id, door_id)

@router.post('/rooms/{room_id}/puzzles/{puzzle_id}/answer')
def answer_puzzle(room_id: str, puzzle_id: str, body: Answer):
    return game_service.answer_puzzle(room_id, puzzle_id, body.answer)

@router.post('/veloci-ruben/ribs')
def give_ribs_to_veloci():
    return game_service.give_ribs_to_veloci()
