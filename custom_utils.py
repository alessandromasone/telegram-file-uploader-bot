import os

# Estensioni comuni per file video e immagine
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

def is_video(file_path):
    """Verifica se il file specificato è un video, controllando l'estensione del file."""
    return os.path.splitext(file_path)[1].lower() in VIDEO_EXTENSIONS

def is_image(file_path):
    """Verifica se il file specificato è un'immagine, controllando l'estensione del file."""
    return os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS

def is_already_processed(file_path, processed_files_path):
    """Verifica se il file è già stato processato"""
    if not os.path.exists(processed_files_path):
        return False  # Se il file di log non esiste, il file non è stato processato

    # Leggi il file di log riga per riga per verificare se il file è già stato processato
    with open(processed_files_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() == file_path:  # Se troviamo una corrispondenza esatta
                return True
    return False

def load_processed_files(processed_files_path):
    """Carica la lista dei file già processati da un file di log."""
    if not os.path.exists(processed_files_path):
        return set()  # Se il file di log non esiste, ritorna un insieme vuoto

    # Leggi i file processati dal file di log, restituendo un set
    with open(processed_files_path, 'r', encoding='utf-8') as file:
        return {line.strip() for line in file if line.strip()}  # Usa un set per evitare duplicati

def save_processed_file(file_path, processed_files_path):
    """Aggiunge un file al log dei file già processati."""
    # Aggiungi il percorso del file al log
    with open(processed_files_path, 'a', encoding='utf-8') as file:
        file.write(f"{file_path}\n")  # Scrivi il percorso del file seguito da una nuova riga
