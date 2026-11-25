import os
import time


def _env_bool(name, default):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# Se true (comportamento originale) un file viene considerato già processato anche
# quando nel txt c'è solo un file con lo STESSO NOME in un'altra cartella.
# Imposta MATCH_BY_FILENAME=false per confrontare solo il percorso completo.
MATCH_BY_FILENAME = _env_bool("MATCH_BY_FILENAME", True)

# Salta i file modificati negli ultimi N secondi (es. ancora in copia). 0 = disattivato.
MIN_FILE_AGE_SECONDS = int(os.environ.get("MIN_FILE_AGE_SECONDS", "0") or 0)

# Estensioni comuni per file video e immagine
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

def is_video(file_path):
    """Verifica se il file specificato è un video, controllando l'estensione del file."""
    return os.path.splitext(file_path)[1].lower() in VIDEO_EXTENSIONS

def is_image(file_path):
    """Verifica se il file specificato è un'immagine, controllando l'estensione del file."""
    return os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS

def load_processed_files(processed_files_path):
    """Carica la lista dei file già processati da un file di log come set di (path, basename)."""
    if not os.path.exists(processed_files_path):
        return set()

    with open(processed_files_path, 'r', encoding='utf-8') as file:
        entries = {line.strip() for line in file if line.strip()}

    # Crea un set che contiene sia i path completi che i basename
    lookup = set()
    for entry in entries:
        lookup.add(entry)
        if MATCH_BY_FILENAME:
            lookup.add(os.path.basename(entry))
    return lookup

def is_already_processed(file_path, processed_set):
    """Verifica se il file è già stato processato usando il set pre-caricato."""
    if file_path in processed_set:
        return True
    return MATCH_BY_FILENAME and os.path.basename(file_path) in processed_set

def save_processed_file(file_path, processed_files_path, processed_set):
    """Aggiunge un file al log dei file già processati e aggiorna il set in memoria."""
    with open(processed_files_path, 'a', encoding='utf-8') as file:
        file.write(f"{file_path}\n")
    processed_set.add(file_path)
    if MATCH_BY_FILENAME:
        processed_set.add(os.path.basename(file_path))

def is_file_stable(file_path):
    """True se il file non è stato modificato negli ultimi MIN_FILE_AGE_SECONDS."""
    if MIN_FILE_AGE_SECONDS <= 0:
        return True
    try:
        return (time.time() - os.path.getmtime(file_path)) >= MIN_FILE_AGE_SECONDS
    except OSError:
        return False
