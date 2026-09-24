from .game_element import GameElement


class Item(GameElement):
    def __init__(self, id: str, name: str, description: str, item_type: str):
        super().__init__(id, name, description)
        self.item_type = item_type

    def to_dict(self):
        return {
            **super().to_dict(),
            "item_type": self.item_type,
        }


class Key(Item):
    def __init__(self, id: str, name: str, description: str):
        super().__init__(id, name, description, "key")


class Ribs(Item):
    def __init__(self, id: str, name: str, description: str, time_add: int):
        self.time_add = time_add
        super().__init__(id, name, description, "ribs")

    def additional_time(self):
        self.duration += self.time_add


ribs = Ribs("ribs", "Ribs", "Ajoute 10min au temps restant", 600)

key = Key("key1", "Key", "Ouvre la porte de la salle 1 vers 2")
kaillou = Key("key2", "Kaillou", "Ouvre la porte de la salle 2 vers 3")
os = Key("key3", "Os", "Ouvre la porte de la salle 3 vers 4")
code = Key("key4", "Code", "Ouvre la porte de la salle 4 vers la sortie " \
            "et dévérrouille les ribs pour Véloci Ruben")
