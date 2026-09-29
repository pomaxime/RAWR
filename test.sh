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
assert_http 200 GET "/"
assert_http 200 GET "/progress"
assert_http 200 GET "/rooms"

# --- Accès et erreurs de salles ---
assert_http 200 GET "/rooms/room_1"
assert_http 403 GET "/rooms/room_2"
assert_http 404 GET "/rooms/salle_inconnue"
assert_contains GET "/rooms/salle_inconnue" 'Salle introuvable'

# --- Vérification du système de ribs au départ ---
assert_http 400 POST "/veloci-ruben/ribs" ''

# --- Réponses invalides de puzzle ---
assert_http 404 POST "/rooms/salle_inconnue/puzzles/puzzle_1/answer" '{"answer":"test"}'
assert_http 404 POST "/rooms/room_1/puzzles/enigme_inconnue/answer" '{"answer":"test"}'
assert_http 422 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{}'
assert_http 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"mauvaise réponse"}'

# --- Réponse correcte de room_1 + progression ---
assert_http 200 POST "/rooms/room_1/puzzles/puzzle_1/answer" '{"answer":"Raptor Affamé Want Ribs"}'
assert_http 200 POST "/rooms/room_1/doors/door_1/open" ''
assert_http 200 GET "/rooms/room_2"
assert_http 403 GET "/rooms/room_3"
assert_contains GET "/progress" '"keys"'
assert_http 200 POST "/veloci-ruben/ribs" ''

# --- Réponse correcte de room_2 + verrouillage suivant ---
assert_http 200 POST "/rooms/room_2/puzzles/puzzle_2/answer" '{"answer":"32"}'
assert_http 200 POST "/rooms/room_2/doors/door_2/open" ''
assert_http 200 GET "/rooms/room_3"
assert_http 403 GET "/rooms/room_4"

# --- Réponse correcte de room_3 + accès room_4 ---
assert_http 200 POST "/rooms/room_3/puzzles/puzzle_3/answer" '{"answer":"RAPTOR"}'
assert_http 200 POST "/rooms/room_3/doors/door_3/open" ''
assert_http 200 GET "/rooms/room_4"

# --- Réponse correcte de room_4 + fin du jeu ---
assert_http 200 POST "/rooms/room_4/puzzles/puzzle_4/answer" '{"answer":"BLEUE"}'
assert_http 200 POST "/rooms/room_4/doors/door_4/open" ''
assert_contains GET "/progress" '"status":"won"'

# --- Documentation automatique FastAPI ---
assert_http 200 GET "/docs"
assert_http 200 GET "/redoc"
assert_http 200 GET "/openapi.json"

echo
echo "Tous les tests sont réussis."
