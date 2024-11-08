import asyncio
import os
from telethon import TelegramClient
from .telegram_video_uploader import upload_video
from .telegram_image_uploader import upload_image
from .file_manager import save_uploaded_file, load_uploaded_files
from .video_processing import split_video

async def create_telegram_client(api_id, api_hash, bot_token=None):
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(bot_token=bot_token) if bot_token else await client.start()
    return client

# Modifiche nella funzione `upload_file`
async def upload_file(client, file_path, group_link, thread_id, video_extensions, image_extensions, max_video_size_mb=2000):
    """Carica il file su Telegram in base all'estensione."""
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Carica i file già caricati dal registro
    uploaded_files = load_uploaded_files()  # Carica l'elenco completo dei file caricati, incluse le parti

    # Controllo dimensione file per i video
    if ext in video_extensions:
        if os.path.getsize(file_path) > max_video_size_mb * 1024**2:  # Converti MB in byte
            print(f"Il file video {filename} supera {max_video_size_mb}MB, verrà suddiviso.")
            parts = split_video(file_path, max_size_mb=max_video_size_mb)
            for part in parts:
                part_name = os.path.basename(part)  # Usa solo il nome del file senza percorso
                
                # Verifica se la parte è già stata caricata
                if part_name in uploaded_files:
                    print(f"Parte {part_name} già caricata, salto...")
                    continue
                
                print(f"Caricamento della parte: {part_name}...")
                success = await upload_video(client, group_link, part, thread_id)
                if success:
                    save_uploaded_file(part_name)  # Salva solo il nome della parte nel registro
                else:
                    print(f"Errore nel caricamento di {part_name}.")
                os.remove(part)  # Rimuove il file temporaneo dopo il caricamento

            # Salva anche il nome del file principale come indicatore che è stato caricato
            save_uploaded_file(filename)
            return True
        else:
            # Se il file non supera la dimensione massima, caricalo direttamente
            print(f"Caricamento del video: {filename}...")
            success = await upload_video(client, group_link, file_path, thread_id)
    elif ext in image_extensions:
        # Carica l'immagine
        print(f"Caricamento dell'immagine: {filename}...")
        success = await upload_image(client, group_link, file_path, thread_id)
    else:
        print(f"File {filename} non supportato (né video né immagine).")
        return False

    # Salva il file se è stato caricato con successo
    if success:
        print(f"{filename} caricato con successo!")
        save_uploaded_file(filename)
    else:
        print(f"Errore nel caricamento di {filename}.")
    return success