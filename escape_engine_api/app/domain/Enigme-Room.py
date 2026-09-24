from .code_puzzle import CodePuzzle
from .room import Room

# ============================================================
# PUZZLE 1
# ============================================================

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


# ============================================================
# ROOM 1
# ============================================================

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


# ============================================================
# PUZZLE 2
# ============================================================

puzzle_2 = CodePuzzle(
    id="puzzle_2",
    name="Le code du miroir noir",
    description=(
        "Un écran s'allume avec une série d'objets sur la table : "
        "4 vis, 3 ampoules, 2 clés et 1 carte. "
        "Le message dit : 'Ordre décroissant des quantités. "
        "Écrivez les chiffres sans espace. Le code est la séquence.' "
        "Quatre chiffres, sans faute.'"
    ),
    secret_code="4321",
    hints=[
        "Le code est construit à partir des nombres visibles sur la table.",
        "Les quantités sont 4, 3, 2, 1 ; il faut les écrire dans l'ordre décroissant.",
        "Le code final est un nombre à 4 chiffres.",
    ],
)


# ============================================================
# ROOM 2
# ============================================================

room_2 = Room(
    id="room_2",
    name="La salle du miroir des ombres",
    description=(
        "Vous pénétrez dans une chambre au plafond bas, aux murs recouverts de "
        "miroirs fissurés. Sur une table, plusieurs objets sont disposés avec précision : "
        "4 vis, 3 ampoules, 2 clés et 1 carte. Une console bloque la sortie, "
        "et un message apparaît : 'Le système demande le code des quantités.'"
    ),
    puzzles=[puzzle_2],
    time_limit=900,
)


# ============================================================
# PUZZLE 3
# ============================================================

puzzle_3 = CodePuzzle(
    id="puzzle_3",
    name="Le générateur délirant",
    description=(
        "Le panneau du générateur affiche : "
        "'3 bras, 5 capteurs, 2 portes, 8 câbles. "
        "Le code est obtenu par (capteurs + portes) × bras - câbles. "
        "Répondez avec le résultat final.' "
        "Le système exige un nombre entier.'"
    ),
    secret_code="13",
    hints=[
        "Le calcul est bien défini sur l'écran : (5 + 2) × 3 - 8.",
        "Commence par additionner les capteurs et les portes.",
        "Le résultat final est un nombre à deux chiffres.",
    ],
)


# ============================================================
# ROOM 3
# ============================================================

room_3 = Room(
    id="room_3",
    name="Le générateur de la salle noire",
    description=(
        "Cette pièce est remplie de câbles torsadés, de capteurs lumineux et de portes "
        "semi-ouvertes. Un panneau de contrôle clignote au centre de la pièce. "
        "La sortie est bloquée par un système qui n'accepte que des calculs précis."
    ),
    puzzles=[puzzle_3],
    time_limit=900,
)


# ============================================================
# PUZZLE 4
# ============================================================

puzzle_4 = CodePuzzle(
    id="puzzle_4",
    name="Le cœur numérique du laboratoire",
    description=(
        "La dernière console affiche : "
        "'1 clé, 3 batteries, 4 cartes, 5 vis et 6 ampoules. "
        "Le code est calculé selon la formule : ((ampoules + vis) × cartes) - (batteries + clé). "
        "Le système attend la valeur exacte.'"
    ),
    secret_code="40",
    hints=[
        "Remplace les mots par les nombres : 6 + 5 = 11, puis × 4.",
        "Ensuite, retirez 3 + 1.",
        "Le code final est un nombre à deux chiffres.",
    ],
)


# ============================================================
# ROOM 4
# ============================================================

room_4 = Room(
    id="room_4",
    name="Le cœur du laboratoire",
    description=(
        "Vous arrivez au cœur du complexe. Les machines sont silencieuses, les lumières "
        "tremblent autour d'un noyau central. Un terminal a remplacé la dernière porte, "
        "et il exige le bon calcul pour libérer votre sortie."
    ),
    puzzles=[puzzle_4],
    time_limit=900,
)


# ============================================================
# ALL ROOMS
# ============================================================

rooms = {
    room_1.id: room_1,
    room_2.id: room_2,
    room_3.id: room_3,
    room_4.id: room_4,
}
