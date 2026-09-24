from .puzzle import Puzzle


class CodePuzzle(Puzzle):
	def __init__(
		self,
		id: str,
		name: str,
		description: str,
		secret_code: str,
		hints: list[str] | None = None,
	):
		super().__init__(id, name, description, hints)
		self.secret_code = secret_code

	def check_solution(self, answer: str) -> bool:
		return answer == self.secret_code
