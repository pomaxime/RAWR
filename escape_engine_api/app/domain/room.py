from .code_puzzle import CodePuzzle
from .game_element import GameElement


class Room(GameElement):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        Items: list | None = None,
        doors: list | None = None,
        puzzles: list | None = None,
        time_limit: int | None = None,
    ):
        super().__init__(id, name, description)
        self.Items = Items or []
        self.doors = doors or []
        self.puzzles = puzzles or []
        self.time_limit = time_limit

    def to_dict(self):
        return {
            **super().to_dict(),
            "Items": self.Items,
            "doors": self.doors,
            "puzzles": self.puzzles,
            "time_limit": self.time_limit,
        }

    def add_item(self, item):
        self.Items.append(item)

    def add_door(self, door):
        self.doors.append(door)

    def add_puzzle(self, puzzle):
        self.puzzles.append(puzzle)


puzzle_1 = CodePuzzle(
    id="puzzle_1",
    name="L'énigme de Véloci Ruben",
    description=(
        "Écrivez la signification de l'inscription RAWR. "
        "<< Rawr, je suis Véloci Ruben le Raptor, j'ai très faim, "
        "beaucoup trop faim. "
        "But i'm going to wait before eating you, Rawr. "
        "Rawr, je veux des côtes. >>"
    ),
    secret_code="Raptor Affamé Want Ribs",
    hints=["Tout vous est donné dans l'ordre des paroles de Véloci Ruben."],
)

room_1 = Room(
    id="room_1",
    name="Le laboratoire de Véloci Ruben",
    description=(
        "Vous êtes enfermés dans un laboratoire rempli de machines étranges "
        "et de dinosaures enfermés. "
        "Une inscription affiche RAWR. "
        "Un Raptor s'approche de vous et vous regarde avec insistance. "
        "Vous entrez dans une pièce avec un ordinateur et un cadenas. "
        "Pour avancer vous devrez trouver la signification de 'RAWR'. "
        "Pour cela, aidez-vous des instructions de Véloci Ruben. "
        "Le raptor vous suit et essaie d'entrer, vous l'entendez parler. "
        "<< Rawr, je suis Véloci Ruben le Raptor, j'ai très faim, "
        "beaucoup trop faim. "
        "But i'm going to wait before eating you. "
        "Rawr, je veux des côtes. >>"
        "Et oui, dans ce jeu tout peut être bilingue."
    ),
    puzzles=[puzzle_1],
    time_limit=900,
)

puzzle_2 = CodePuzzle(
    id="puzzle_2",
    name="Le terminal du laboratoire",
    description=(
        "Vous arrivez dans une salle remplie d'ordinateurs. "
        "Un terminal vous demande de trouver le nombre suivant : "
        "2 - 4 - 8 - 16 - ? "
        "Une inscription est affichée sous l'écran : "
        '"Dans ce laboratoire, tout double."'
        '"Dans ce laboratoire, tout double."'
    ),
    secret_code="32",
    hints=[
        "Observez la relation entre chaque nombre.",
        "Chaque nombre est obtenu à partir du précédent.",
        "Le nombre suivant est le double de 16.",
        "Le nombre suivant est le double de 16.",
    ],
)

room_2 = Room(
    id="room_2",
    name="La salle des ordinateurs",
    description=(
        "La porte du laboratoire s'ouvre et vous découvrez une immense "
        "salle remplie d'ordinateurs. "
        "Au centre de la pièce, un vieux terminal clignote. "
        "Un message apparaît à l'écran : "
        '"Seul celui qui comprend la suite pourra continuer."'
        '"Seul celui qui comprend la suite pourra continuer."'
    ),
    puzzles=[puzzle_2],
    time_limit=900,
)

puzzle_3 = CodePuzzle(
    id="puzzle_3",
    name="Le message crypté",
    description=(
        "Sur un bureau, vous trouvez une feuille couverte de lettres : "
        '"UDSWRU" '
        '"UDSWRU" '
        "Une note est écrite en dessous : "
        '"Véloci Ruben a déplacé chaque lettre de trois positions '
        '"Véloci Ruben a déplacé chaque lettre de trois positions '
        "dans l'alphabet.\" "
        "Déchiffrez le message."
    ),
    secret_code="RAPTOR",
    hints=[
        "Les lettres ont été déplacées dans l'alphabet.",
        "Il faut reculer de trois lettres.",
        "U devient R.",
        "U devient R.",
    ],
)

room_3 = Room(
    id="room_3",
    name="La salle de cryptographie",
    description=(
        "Vous entrez dans une pièce sombre dont les murs sont couverts "
        "de vieux messages codés. "
        "Une seule feuille semble récente. "
        "Vous comprenez rapidement qu'elle contient un message laissé "
        "par Véloci Ruben."
    ),
    puzzles=[puzzle_3],
    time_limit=900,
)

puzzle_4 = CodePuzzle(
    id="puzzle_4",
    name="Les cages des dinosaures",
    description=(
        "Trois cages se trouvent devant vous : "
        "une cage rouge, une cage bleue et une cage verte. "
        "Une seule contient la clé permettant de continuer. "
        "Sur les cages, vous trouvez trois inscriptions : "
        '"La clé n\'est pas dans la cage rouge." '
        '"La clé est dans la cage rouge." '
        '"La clé n\'est pas dans la cage bleue." '
        '"La clé n\'est pas dans la cage rouge." '
        '"La clé est dans la cage rouge." '
        '"La clé n\'est pas dans la cage bleue." '
        "Une seule de ces affirmations est vraie. "
        "Dans quelle cage se trouve la clé ?"
    ),
    secret_code="BLEUE",
    hints=[
        "Une seule affirmation est vraie.",
        "Testez les trois possibilités.",
        "Si la clé est dans la cage bleue, une seule affirmation est vraie.",
        "Si la clé est dans la cage bleue, une seule affirmation est vraie.",
    ],
)

room_4 = Room(
    id="room_4",
    name="La salle des cages",
    description=(
        "Vous arrivez dans une immense salle contenant plusieurs cages. "
        "Certaines sont vides, tandis que d'autres contiennent "
        "des dinosaures endormis. "
        "Trois cages attirent votre attention. "
        "Une clé se trouve dans l'une d'elles, mais vous devez déterminer "
        "laquelle avant de pouvoir atteindre la sortie."
    ),
    puzzles=[puzzle_4],
    time_limit=900,
)
