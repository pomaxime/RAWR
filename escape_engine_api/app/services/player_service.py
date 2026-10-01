from ..errors import AppError
from ..models.player import Player

class PlayerService:
    def __init__(self):
        self.players = []

    def get_players(self):
        return self.players

    def get_player(self, player_id: int):
        player = next((item for item in self.players if item['id'] == player_id), None)
        if player is None:
            raise AppError(status_code=404, detail='Player not found')
        return player

    def create_player(self, player: Player):
        next_id = max((item['id'] for item in self.players), default=0) + 1
        new_player = {'id': next_id, **player.model_dump()}
        self.players.append(new_player)
        return new_player

    def update_player(self, player_id: int, player: Player):
        for index, current_player in enumerate(self.players):
            if current_player['id'] == player_id:
                updated_player = {'id': player_id, **player.model_dump()}
                self.players[index] = updated_player
                return updated_player
        raise AppError(status_code=404, detail='Player not found')

    def delete_player(self, player_id: int):
        for index, current_player in enumerate(self.players):
            if current_player['id'] == player_id:
                deleted_player = self.players.pop(index)
                return {'message': 'Player deleted', 'player': deleted_player}
        raise AppError(status_code=404, detail='Player not found')

player_service = PlayerService()
