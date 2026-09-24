import hashlib

from .puzzle import Puzzle


class HashPuzzle(Puzzle):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        expected_hash: str,
        hints: list[str] | None = None,
    ):
        super().__init__(id, name, description, hints)
        self.expected_hash = expected_hash

    def check_solution(self, answer: str) -> bool:
        answer_hash = hashlib.sha256(answer.encode()).hexdigest()
        return answer_hash == self.expected_hash
