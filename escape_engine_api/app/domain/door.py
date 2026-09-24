from .game_element import GameElement


class Door(GameElement):
	def __init__(
		self,
		id: str,
		name: str,
		description: str,
		is_locked: bool = True,
		required_item_id: str | None = None,
		destination_room_id: str | None = None,
	):
		super().__init__(id, name, description)
		self.is_locked = is_locked
		self.required_item_id = required_item_id
		self.destination_room_id = destination_room_id

	def open_door(self, inventory: list) -> str | None:
		if not self.is_locked:
			return self.destination_room_id

		if any(item.id == self.required_item_id for item in inventory):
			self.is_locked = False
			return self.destination_room_id
		else:
			self.is_locked = True
			return None