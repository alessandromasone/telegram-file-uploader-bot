#!/bin/bash

# Verifica se la cartella "env" esiste
if [ ! -d "env" ]; then
    echo "L'ambiente virtuale non esiste, lo creo..."
    python3 -m venv env
    echo "Ambiente virtuale creato."
fi

# Attiva l'ambiente virtuale
source ./env/bin/activate
