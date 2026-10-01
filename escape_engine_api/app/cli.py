from .services.game_service import game_service

def play_game() -> None:
    print('=== RAWR Escape Game ===')
    print("Résolvez les salles dans l'ordre pour obtenir les clés et débloquer la suite.")
    print('Commandes : aide, quitter')
    for room in game_service.rooms:
        if not game_service.can_access_room(room.id):
            print(f'\nLa salle {room.name} est verrouillée. Vous devez terminer la salle précédente.')
            break
        print(f'\n=== {room.name} ===')
        print(room.description)
        puzzle = room.puzzles[0] if room.puzzles else None
        if puzzle is None:
            print('Aucune énigme dans cette salle.')
            continue
        print(f'\nÉnigme : {puzzle.name}')
        print(puzzle.description)
        for attempt in range(1, 4):
            answer = input('Votre réponse : ').strip()
            if answer.lower() in {'quitter', 'quit', 'exit'}:
                print('Partie interrompue.')
                return
            if answer.lower() in {'aide', 'help', 'indice'}:
                if puzzle.hints:
                    print('Indices :')
                    for hint_index, hint in enumerate(puzzle.hints, start=1):
                        print(f'  {hint_index}. {hint}')
                else:
                    print('Aucun indice disponible.')
                continue
            result = game_service.answer_console_puzzle(room.id, puzzle.id, answer)
            if result["correct"]:
                print("Bonne réponse !")
                print(f'La clé de la salle {room.name} a été validée. La salle suivante est déverrouillée.')
                break
            remaining = 3 - attempt
            print(f'Mauvaise réponse. Il vous reste {remaining} tentative(s).')
            if attempt == 3:
                print("Vous n'avez plus de tentatives. Partie terminée.")
                return
    if game_service.progress['unlocked_index'] >= len(game_service.rooms) - 1:
        print('\nFélicitations ! Vous avez terminé le jeu et débloqué toutes les salles.')

if __name__ == "__main__":
    play_game()
