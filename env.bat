@echo off

:: Verifica se la cartella "env" esiste
if not exist "env/Scripts/activate.bat" (
    echo L'ambiente virtuale non esiste, lo creo...
    python -m venv env
    echo Ambiente virtuale creato, lo attivo...
)

:: Attiva l'ambiente virtuale
call env/Scripts/activate