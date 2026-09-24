class GameElement:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description

    def interact(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}