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
        lookup.add(os.path.basename(entry))
    return lookup

def is_already_processed(file_path, processed_set):
    """Verifica se il file è già stato processato usando il set pre-caricato."""
    file_name = os.path.basename(file_path)
    return file_path in processed_set or file_name in processed_set

def save_processed_file(file_path, processed_files_path, processed_set):
    """Aggiunge un file al log dei file già processati e aggiorna il set in memoria."""
    with open(processed_files_path, 'a', encoding='utf-8') as file:
        file.write(f"{file_path}\n")
    processed_set.add(file_path)
    processed_set.add(os.path.basename(file_path))
