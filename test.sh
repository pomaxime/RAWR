#!/bin/bash

# Adresse de l'API. Vous pouvez la changer si le serveur utilise un autre port.
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

# Envoie une requête et vérifie son code HTTP.
# Exemple : tester 200 GET /rooms
tester() {
    code_attendu="$1"
    methode="$2"
    chemin="$3"
    donnees="$4"

    if [ -n "$donnees" ]; then
        code_recu=$(curl -s -o /dev/null -w "%{http_code}" \
            -X "$methode" \
            -H "Content-Type: application/json" \
            -d "$donnees" \
            "$BASE_URL$chemin")
    else
        code_recu=$(curl -s -o /dev/null -w "%{http_code}" \
            -X "$methode" "$BASE_URL$chemin")
    fi

    if [ "$code_recu" = "$code_attendu" ]; then
        echo "OK     $methode $chemin : HTTP $code_recu"
    else
        echo "ERREUR $methode $chemin : HTTP $code_recu au lieu de $code_attendu"
        exit 1
    fi
}

echo "Tests de l'API RAWR : $BASE_URL"
echo "Redémarrez le serveur avant le test pour réinitialiser la progression."
echo

# Routes générales
tester 200 GET "/" ""
tester 200 GET "/progress" ""
tester 200 GET "/rooms" ""

# Accès aux salles : la première est ouverte, la deuxième est verrouillée au départ.
tester 200 GET "/rooms/room_1" ""
tester 403 GET "/rooms/room_2" ""
tester 404 GET "/rooms/salle_inconnue" ""

# Vérification des erreurs lors de l'envoi d'une réponse.
tester 404 POST "/rooms/salle_inconnue/puzzles/puzzle_1/answer" '{"answer":"test"}'
tester 404 POST "/rooms/room_1/puzzles/enigme_inconnue/answer" '{"answer":"test"}'
tester 422 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{}'
tester 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"mauvaise réponse"}'

# Parcours complet : chaque bonne réponse débloque la salle suivante.
tester 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"Raptor Affamé Want Ribs"}'
tester 200 GET "/rooms/room_2" ""
tester 200 POST "/rooms/room_2/puzzles/puzzle_2/answer" '{"answer":"32"}'
tester 200 GET "/rooms/room_3" ""
tester 200 POST "/rooms/room_3/puzzles/puzzle_3/answer" '{"answer":"RAPTOR"}'
tester 200 GET "/rooms/room_4" ""
tester 200 POST "/rooms/room_4/puzzles/puzzle_4/answer" '{"answer":"BLEUE"}'

# Documentation automatique de FastAPI
tester 200 GET "/docs" ""
tester 200 GET "/redoc" ""
tester 200 GET "/openapi.json" ""

echo
echo "Tous les tests sont réussis."
