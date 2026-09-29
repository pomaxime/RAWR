from __future__ import annotations

import logging

from ..domain.room import room_1, room_2, room_3, room_4
from ..domain.time import Time
from ..errors import EmptyAnswerError, PuzzleNotFoundError, RoomLockedError, RoomNotFoundError

logger = logging.getLogger(__name__)


class GameService:
    def __init__(self):
        self.rooms = [room_1, room_2, room_3, room_4]
        self.progress = {
            "unlocked_index": 0,
            "completed": [],
            "keys": [],
        }
        self.game_timer = Time.from_room(room_1)
        logger.info("GameService initialisé avec %s salles", len(self.rooms))

    def get_room_index(self, room_id: str):
        for index, room in enumerate(self.rooms):
            if room.id == room_id:
                logger.debug("Salle %s trouvée à l'index %s", room_id, index)
                return index
        logger.debug("Salle %s introuvable", room_id)
        return None

    def get_room(self, room_id: str):
        room = next((room for room in self.rooms if room.id == room_id), None)
        if room is None:
            logger.debug("get_room: salle %s absente", room_id)
        return room

    def can_access_room(self, room_id: str) -> bool:
        room_index = self.get_room_index(room_id)
        if room_index is None:
            logger.debug("Accès refusé à %s: salle inconnue", room_id)
            return False
        room = self.rooms[room_index]
        has_access = room.required_key_id is None or any(
            item["id"] == room.required_key_id for item in self.progress["keys"]
        )
        logger.debug(
            "Accès room=%s => %s (clé requise=%s, clés=%s)",
            room_id,
            has_access,
            room.required_key_id,
            self.progress["keys"],
        )
        return has_access

    def ensure_room_access(self, room_id: str):
        room = self.get_room(room_id)
        if room is None:
            logger.warning("Tentative d'accès à une salle inconnue: %s", room_id)
            raise RoomNotFoundError()
        if not self.can_access_room(room_id):
            logger.warning("Tentative d'accès à une salle verrouillée: %s", room_id)
            raise RoomLockedError()
        logger.debug("Accès autorisé à la salle %s", room_id)
        return room

    def get_progress(self):
        progress = {
            "unlocked_index": self.progress["unlocked_index"],
            "completed": self.progress["completed"],
            "keys": self.progress["keys"],
            "remaining_time": self.game_timer.remaining(),
            "next_room": next(
                (
                    room.id
                    for room in self.rooms
                    if self.can_access_room(room.id)
                    and room.id not in self.progress["completed"]
                ),
                None,
            ),
        }
        logger.debug("Progression demandée: %s", progress)
        return progress

    def get_rooms(self):
        rooms_payload = [
            {
                "id": room.id,
                "name": room.name,
                "description": room.description,
                "locked": not self.can_access_room(room.id),
            }
            for room in self.rooms
        ]
        logger.debug("Liste des salles renvoyée: %s", rooms_payload)
        return rooms_payload

    def get_room_detail(self, room_id: str):
        room = self.ensure_room_access(room_id)
        if not self.game_timer.running:
            self.game_timer.start()
            logger.info("Timer démarré pour la salle %s", room_id)
        payload = {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "puzzles": [
                {
                    "id": puzzle.id,
                    "name": puzzle.name,
                    "description": puzzle.description,
                    "hints": puzzle.hints,
                }
                for puzzle in room.puzzles
            ],
            "required_key_id": room.required_key_id,
        }
        logger.debug("Détail salle %s: %s", room_id, payload)
        return payload

    def answer_puzzle(self, room_id: str, puzzle_id: str, answer: str):
        room = self.ensure_room_access(room_id)
        puzzle = next((item for item in room.puzzles if item.id == puzzle_id), None)
        if puzzle is None:
            logger.warning("Énigme %s introuvable pour la salle %s", puzzle_id, room_id)
            raise PuzzleNotFoundError()
        if not answer or not answer.strip():
            logger.warning("Réponse vide soumise pour room=%s puzzle=%s", room_id, puzzle_id)
            raise EmptyAnswerError()

        is_correct = puzzle.check_solution(answer)
        logger.info(
            "Résultat réponse room=%s puzzle=%s: %s (réponse='%s')",
            room_id,
            puzzle_id,
            is_correct,
            answer,
        )
        obtained_key = None
        if is_correct:
            room_index = self.get_room_index(room_id)
            if room_index is not None and room_id not in self.progress["completed"]:
                self.progress["completed"].append(room_id)
            if room.reward_key and not any(
                item["id"] == room.reward_key.id for item in self.progress["keys"]
            ):
                obtained_key = room.reward_key.to_dict()
                self.progress["keys"].append(obtained_key)
                logger.info("Nouvelle clé obtenue: %s", obtained_key)
            if room_index is not None and room_index + 1 < len(self.rooms):
                self.progress["unlocked_index"] = room_index + 1
                if self.can_access_room(self.rooms[room_index + 1].id):
                    self.game_timer.continue_to_room(self.rooms[room_index + 1])
                    logger.info(
                        "Timer réinitialisé et salle suivante ouverte: %s",
                        self.rooms[room_index + 1].id,
                    )
            else:
                self.progress["unlocked_index"] = len(self.rooms) - 1

        result = {"correct": is_correct, "obtained_key": obtained_key, "progress": self.progress}
        logger.debug("Réponse traitée: %s", result)
        return result


game_service = GameService()
