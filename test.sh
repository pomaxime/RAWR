#!/bin/bash

# Adresse de l'API. Tu peux la changer si le serveur n'écoute pas sur 8000.
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

# Capture une réponse HTTP avec son body.
# Usage: request "GET" "/rooms" ""
request() {
    method="$1"
    path="$2"
    body="${3:-}"
    temp_file="$(mktemp)"

    if [ -n "$body" ]; then
        curl -sS -D "$temp_file.headers" -o "$temp_file.body" \
            -X "$method" \
            -H "Content-Type: application/json" \
            -d "$body" \
            "$BASE_URL$path"
    else
        curl -sS -D "$temp_file.headers" -o "$temp_file.body" \
            -X "$method" \
            "$BASE_URL$path"
    fi

    status=$(awk 'BEGIN{code=""} /^HTTP\// {code=$2} END {print code}' "$temp_file.headers")
    body_content=$(cat "$temp_file.body")

    echo "$status|$body_content"
    rm -f "$temp_file" "$temp_file.headers" "$temp_file.body"
}

# Vérifie un code HTTP attendu.
assert_http() {
    expected="$1"
    method="$2"
    path="$3"
    body="${4:-}"
    response="$(request "$method" "$path" "$body")"
    status="${response%%|*}"
    payload="${response#*|}"

    if [ "$status" = "$expected" ]; then
        echo "OK     $method $path : HTTP $status"
    else
        echo "ERREUR $method $path : HTTP $status au lieu de $expected"
        echo "$payload"
        exit 1
    fi
}

# Vérifie qu'une chaîne est présente dans la réponse.
assert_contains() {
    method="$1"
    path="$2"
    needle="$3"
    body="${4:-}"
    response="$(request "$method" "$path" "$body")"
    status="${response%%|*}"
    payload="${response#*|}"

    if printf '%s' "$payload" | grep -Fq "$needle"; then
        echo "OK     $method $path : contient '$needle'"
    else
        echo "ERREUR $method $path : '$needle' absent"
        echo "$payload"
        exit 1
    fi
}

echo "Tests de l'API RAWR : $BASE_URL"
echo "Redémarrez le serveur avant le test pour réinitialiser la progression."
echo

# --- Routes générales ---
# Vérifie que l'accueil de l'API répond correctement.
assert_http 200 GET "/"
# Vérifie que l'état actuel de la partie est accessible.
assert_http 200 GET "/progress"
# Vérifie que la liste des salles est accessible.
assert_http 200 GET "/rooms"

# --- Accès et erreurs de salles ---
# La première salle est accessible dès le début.
assert_http 200 GET "/rooms/room_1"
# La deuxième salle est verrouillée tant que la première énigme n'est pas résolue.
assert_http 403 GET "/rooms/room_2"
# Une salle qui n'existe pas doit renvoyer une erreur 404.
assert_http 404 GET "/rooms/salle_inconnue"
# Vérifie que le message d'erreur indique que la salle est introuvable.
assert_contains GET "/rooms/salle_inconnue" 'Salle introuvable'

# --- Vérification du système de ribs au départ ---
# Sans avoir terminé l'énigme requise, l'API refuse la demande de ribs.
assert_http 400 POST "/veloci-ruben/ribs" ''

# --- Réponses invalides de puzzle ---
# Une salle inconnue ne peut pas recevoir de réponse à une énigme.
assert_http 404 POST "/rooms/salle_inconnue/puzzles/puzzle_1/answer" '{"answer":"test"}'
# Un identifiant d'énigme inconnu doit renvoyer une erreur 404.
assert_http 404 POST "/rooms/room_1/puzzles/enigme_inconnue/answer" '{"answer":"test"}'
# Le champ answer est obligatoire : un corps vide est rejeté par validation.
assert_http 422 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{}'
# Une réponse incorrecte est traitée normalement par l'API.
assert_http 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"mauvaise réponse"}'

# --- Réponse correcte de room_1 + progression ---
# Résout l'énigme de la première salle.
assert_http 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"Raptor Affamé Want Ribs"}'
# Ouvre la porte de la première salle après la résolution.
assert_http 200 POST "/rooms/room_1/doors/door_1/open" ''
# Vérifie que la deuxième salle est maintenant accessible.
assert_http 200 GET "/rooms/room_2"
# La troisième salle reste verrouillée à ce stade.
assert_http 403 GET "/rooms/room_3"
# Vérifie que la progression expose bien les clés obtenues.
assert_contains GET "/progress" '"keys"'
# Réclame les ribs, désormais disponibles après la première énigme.
assert_http 200 POST "/veloci-ruben/ribs" ''

# --- Réponse correcte de room_2 + verrouillage suivant ---
# Résout l'énigme de la deuxième salle.
assert_http 200 POST "/rooms/room_2/puzzles/puzzle_2/answer" '{"answer":"32"}'
# Ouvre la porte de la deuxième salle.
assert_http 200 POST "/rooms/room_2/doors/door_2/open" ''
# Vérifie que la troisième salle est accessible.
assert_http 200 GET "/rooms/room_3"
# La quatrième salle reste verrouillée jusqu'à la résolution de la troisième.
assert_http 403 GET "/rooms/room_4"

# --- Réponse correcte de room_3 + accès room_4 ---
# Résout l'énigme de la troisième salle.
assert_http 200 POST "/rooms/room_3/puzzles/puzzle_3/answer" '{"answer":"RAPTOR"}'
# Ouvre la porte de la troisième salle.
assert_http 200 POST "/rooms/room_3/doors/door_3/open" ''
# Vérifie que la quatrième salle est maintenant accessible.
assert_http 200 GET "/rooms/room_4"

# --- Réponse correcte de room_4 + fin du jeu ---
# Résout l'énigme finale.
assert_http 200 POST "/rooms/room_4/puzzles/puzzle_4/answer" '{"answer":"BLEUE"}'
# Ouvre la dernière porte pour terminer la partie.
assert_http 200 POST "/rooms/room_4/doors/door_4/open" ''
# Vérifie que l'état de la partie indique une victoire.
assert_contains GET "/progress" '"status":"won"'

# --- Documentation automatique FastAPI ---
# Vérifie que la documentation Swagger est disponible.
assert_http 200 GET "/docs"
# Vérifie que la documentation ReDoc est disponible.
assert_http 200 GET "/redoc"
# Vérifie que le schéma OpenAPI est disponible.
assert_http 200 GET "/openapi.json"

echo
echo "Tous les tests sont réussis."
