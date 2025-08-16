import os
import json
import asyncio
import yaml
import argparse
from video_utils import extract_thumbnail
from telegram_utils import upload_video_to_telegram, upload_image_to_telegram, initialize_telegram_client
from custom_utils import is_image, is_video, load_processed_files, save_processed_file, is_already_processed

# Variabili globali
config = None
client = None

async def handle_video(file_path):
    """Gestisce il caricamento di un video su Telegram."""
    global client
    print(f"Video trovato: {file_path}")

    # Inizializza variabili
    thumbnail_path = None
    caption = None

    # Estrazione della thumbnail, se configurato
    if config["VIDEO_THUMBNAIL"]:
        thumbnail_path = extract_thumbnail(file_path)

    # Impostazione della didascalia, se configurato
    if config["VIDEO_CAPTION"]:
        caption = os.path.splitext(os.path.basename(file_path))[0]

    # Parametri per il caricamento
    supports_streaming = config["SUPPORT_VIDEO_STREAMING"]
    show_progress = config["SHOW_PROGRESS_BAR"]
    reply_to_message_id = config["REPLY_ID"]

    # Upload del video su Telegram
    success = await upload_video_to_telegram(
        client=client,
        group_link=config["GROUP_LINK"],
        video_path=file_path,
        thumbnail_path=thumbnail_path,
        supports_streaming=supports_streaming,
        show_progress=show_progress,
        caption=caption,
        reply_to_message_id=reply_to_message_id
    )

    # Pulizia della thumbnail se è stata estratta
    if thumbnail_path and os.path.isfile(thumbnail_path):
        os.remove(thumbnail_path)

    # Eliminazione del video dopo l'upload se configurato
    if config["DELETE_AFTER_UPLOAD"] and os.path.isfile(file_path) and success:
        os.remove(file_path)

    # Risultato del caricamento
    print("Caricamento video completato!" if success else "Caricamento fallito.")
    return success

async def handle_image(file_path):
    """Gestisce un'immagine (da implementare)."""
    global client
    print(f"Immagine trovata: {file_path}")
    
    # Inizializza variabili
    caption = None

    # Impostazione della didascalia, se configurato
    if config["IMAGE_CAPTION"]:
        caption = os.path.splitext(os.path.basename(file_path))[0]

    # Parametri per il caricamento
    show_progress = config["SHOW_PROGRESS_BAR"]
    reply_to_message_id = config["REPLY_ID"]

    # Upload dell'immagine su Telegram
    success = await upload_image_to_telegram(
        client=client,
        group_link=config["GROUP_LINK"],
        image_path=file_path,
        show_progress=show_progress,
        caption=caption,
        reply_to_message_id=reply_to_message_id
    )

    # Eliminazione del video dopo l'upload se configurato
    if config["DELETE_AFTER_UPLOAD"] and os.path.isfile(file_path) and success:
        os.remove(file_path)

    # Risultato del caricamento
    print("Caricamento immagine completato!" if success else "Caricamento fallito.")
    return success

async def process_file(file_path):
    """Gestisce un file in base al tipo, se non è già stato processato."""
    
    # Controlla se il file è già stato processato
    if is_already_processed(file_path, config["PROCESSED_FILES_PATH"]):
        print(f"Già processato, salto: {file_path}")
        return

    # Gestione del video
    if is_video(file_path):
        success = await handle_video(file_path)
        if success:
            save_processed_file(file_path, config["PROCESSED_FILES_PATH"])

    # Gestione dell'immagine
    elif is_image(file_path):
        success = await handle_image(file_path)
        if success:
            save_processed_file(file_path, config["PROCESSED_FILES_PATH"])

    # Gestione dei file non supportati
    else:
        print(f"Skippato (tipo non supportato): {file_path}")

async def process_folder(folder):
    """Processa tutti i file all'interno della cartella."""
    
    # Verifica se la cartella esiste
    if not os.path.isdir(folder):
        print(f"Errore: la cartella {folder} non esiste.")
        return

    # Inizia l'elaborazione dei file nella cartella
    print(f"Controllando la cartella: {folder}")
    
    # Itera attraverso tutti i file nella cartella
    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)
        
        # Solo i file vengono processati, non le cartelle
        if os.path.isfile(full_path):
            # Elabora il file
            await process_file(full_path)

# Funzione principale
async def main():
    global client, config

    # Parsing degli argomenti da linea di comando
    parser = argparse.ArgumentParser(description="Carica e processa video su Telegram.")
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help="Percorso del file di configurazione YAML (default: 'config.yaml')"
    )
    parser.add_argument(
        '--session',
        type=str,
        default='session.session',
        help="Nome del file di sessione Telethon (default: 'session.session')"
    )
    args = parser.parse_args()

    # Carica la configurazione dal file YAML
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"Errore: Il file di configurazione '{config_path}' non esiste.")
        return

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Verifica se ci sono cartelle da processare
    folders = config.get("FOLDERS", [])
    if not folders:
        print("Errore: nessuna cartella configurata.")
        return

    # Inizializza il client Telegram con il token, credenziali e nome file di sessione
    client = await initialize_telegram_client(
        config["BOT_TOKEN"],
        config["API_ID"],
        config["API_HASH"],
        session_file=args.session
    )

    # Processa ogni cartella configurata
    for folder in folders:
        await process_folder(folder)
    
    # Chiudi il client (importantissimo!)
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
