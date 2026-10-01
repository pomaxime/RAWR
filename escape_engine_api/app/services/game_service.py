from copy import deepcopy
from ..models.item import code, kaillou, key, os
from ..models.room import room_1, room_2, room_3, room_4
from ..models.time import Time
from ..errors import AppError

class GameService:
    def __init__(self):
        self.rooms = deepcopy([room_1, room_2, room_3, room_4])
        self.progress = {"unlocked_index": 0, "completed": [], "keys": [], "ribs": 0, "status": "playing"}
        self.game_timer = Time.from_room(self.rooms[0])
        self.inventory_items = {item.id: item for item in (key, kaillou, os, code)}

    def refresh_game_status(self):
        if self.progress['status'] == 'playing' and self.game_timer.remaining() <= 0:
            self.progress['status'] = 'lost'
            self.game_timer.stop()
        return self.progress['status']

    def require_active_game(self):
        status = self.refresh_game_status()
        if status == 'lost':
            raise AppError(status_code=409, detail='Partie perdue : le temps est écoulé.')
        if status == 'won':
            raise AppError(status_code=409, detail='La partie est déjà terminée.')

    def get_room_index(self, room_id: str):
        for index, room in enumerate(self.rooms):
            if room.id == room_id:
                return index
        return None

    def can_access_room(self, room_id: str) -> bool:
        room_index = self.get_room_index(room_id)
        if room_index is None:
            return False
        room = self.rooms[room_index]
        return room.required_key_id is None or any((item['id'] == room.required_key_id for item in self.progress['keys']))

    def get_progress(self):
        self.refresh_game_status()
        return {'unlocked_index': self.progress['unlocked_index'], 'completed': self.progress['completed'], 'keys': self.progress['keys'], 'ribs': self.progress['ribs'], 'status': self.progress['status'], 'remaining_time': self.game_timer.remaining(), 'next_room': next((room.id for room in self.rooms if self.can_access_room(room.id) and room.id not in self.progress['completed']), None)}

    def get_rooms(self):
        self.refresh_game_status()
        return [{'id': r.id, 'name': r.name, 'description': r.description, 'locked': not self.can_access_room(r.id), 'doors': [door.to_dict() for door in r.doors]} for r in self.rooms]

    def get_room(self, room_id: str):
        self.require_active_game()
        room = next((r for r in self.rooms if r.id == room_id), None)
        if room is None:
            raise AppError(status_code=404, detail='Salle introuvable')
        if not self.can_access_room(room_id):
            raise AppError(status_code=403, detail='Cette salle est verrouillée. Résolvez les salles précédentes pour débloquer la suite.')
        if not self.game_timer.running:
            self.game_timer.start()
        return {'id': room.id, 'name': room.name, 'description': room.description, 'puzzles': [{'id': p.id, 'name': p.name, 'description': p.description, 'hints': p.hints} for p in room.puzzles], 'required_key_id': room.required_key_id, 'doors': [door.to_dict() for door in room.doors]}

    def open_room_door(self, room_id: str, door_id: str):
        self.require_active_game()
        room = next((r for r in self.rooms if r.id == room_id), None)
        if room is None:
            raise AppError(status_code=404, detail='Salle introuvable')
        if not self.can_access_room(room_id):
            raise AppError(status_code=403, detail='Cette salle est verrouillée.')
        door = next((item for item in room.doors if item.id == door_id), None)
        if door is None:
            raise AppError(status_code=404, detail='Porte introuvable')
        inventory = [self.inventory_items[item['id']] for item in self.progress['keys']]
        destination = door.open_door(inventory)
        if destination is None:
            raise AppError(status_code=403, detail='Il vous manque la clé de cette porte.')
        if destination == 'exit':
            self.progress['status'] = 'won'
            self.game_timer.stop()
        return {'opened': True, 'destination_room_id': destination, 'door': door.to_dict()}

    def answer_puzzle(self, room_id: str, puzzle_id: str, answer: str):
        self.require_active_game()
        room = next((r for r in self.rooms if r.id == room_id), None)
        if room is None:
            raise AppError(status_code=404, detail='Salle introuvable')
        if not self.can_access_room(room_id):
            raise AppError(status_code=403, detail='Cette salle est verrouillée. Résolvez les salles précédentes pour débloquer la suite.')
        puzzle = next((p for p in room.puzzles if p.id == puzzle_id), None)
        if puzzle is None:
            raise AppError(status_code=404, detail='Énigme introuvable')
        is_correct = puzzle.check_solution(answer)
        obtained_key = None
        next_room = None
        message = 'Mauvaise réponse. Essayez encore.'
        if is_correct:
            room_index = self.get_room_index(room_id)
            if room_index is not None and room_id not in self.progress['completed']:
                self.progress['completed'].append(room_id)
            if room.reward_key and (not any((item['id'] == room.reward_key.id for item in self.progress['keys']))):
                obtained_key = room.reward_key.to_dict()
                self.progress['keys'].append(obtained_key)
            self.progress['ribs'] += 1
            if room_index is not None and room_index + 1 < len(self.rooms):
                self.progress['unlocked_index'] = room_index + 1
                following_room = self.rooms[room_index + 1]
                if self.can_access_room(following_room.id):
                    self.game_timer.continue_to_room(following_room)
                    next_room = {'id': following_room.id, 'name': following_room.name, 'url': f'/rooms/{following_room.id}'}
            else:
                self.progress['unlocked_index'] = len(self.rooms) - 1
            found_item = room.reward_key.name if room.reward_key else "l'objet de la salle"
            if next_room:
                message = f"Vous avez réussi et trouvé {found_item}. Vous pouvez entrer dans la salle suivante : {next_room['name']}."
            else:
                message = f'Vous avez réussi et trouvé {found_item}. Vous pouvez maintenant ouvrir la porte de sortie.'

        return {'correct': is_correct, 'message': message, 'obtained_key': obtained_key, 'next_room': next_room, 'progress': self.progress}

    def give_ribs_to_veloci(self):
        self.require_active_game()
        if self.progress['ribs'] <= 0:
            raise AppError(status_code=400, detail="Vous n'avez aucun ribs disponible.")
        self.progress['ribs'] -= 1
        self.game_timer.add_time(600)
        return {'message': 'Véloci Ruben a reçu un ribs.', 'added_time': 600, 'remaining_time': self.game_timer.remaining(), 'ribs': self.progress['ribs']}

    def answer_console_puzzle(self, room_id: str, puzzle_id: str, answer: str):
        self.get_room(room_id)
        room = next(room for room in self.rooms if room.id == room_id)
        puzzle = next((p for p in room.puzzles if p.id == puzzle_id), None)
        if puzzle is None:
            raise AppError(status_code=404, detail="Énigme introuvable")
        if hasattr(puzzle, "secret_code") and answer.lower() == puzzle.secret_code.lower():
            answer = puzzle.secret_code
        return self.answer_puzzle(room_id, puzzle_id, answer)


game_service = GameService()
