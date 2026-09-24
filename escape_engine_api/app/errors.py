class AppError(Exception):
    status_code = 500
    detail = "Une erreur inconnue s'est produite."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class RoomNotFoundError(AppError):
    status_code = 404
    detail = "Salle introuvable"


class RoomLockedError(AppError):
    status_code = 403
    detail = "Cette salle est verrouillée. Résolvez les salles précédentes pour débloquer la suite."


class PuzzleNotFoundError(AppError):
    status_code = 404
    detail = "Énigme introuvable"


class EmptyAnswerError(AppError):
    status_code = 400
    detail = "La réponse ne peut pas être vide."
