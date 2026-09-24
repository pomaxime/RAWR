from .game_element import GameElement


class Puzzle(GameElement):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        hints: list[str] | None = None,
    ):
        super().__init__(id, name, description)
        self.hints = hints or []

    def add_hint(self, hint: str) -> None:
        self.hints.append(hint)

    def get_hint(self, index: int) -> str | None:
        if 0 <= index < len(self.hints):
            return self.hints[index]
        return None

    def check_solution(self, answer: str) -> bool:
        raise NotImplementedError