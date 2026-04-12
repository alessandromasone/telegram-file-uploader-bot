import os
import asyncio
import yaml
import argparse
from video_utils import extract_thumbnail
from telegram_utils import upload_video_to_telegram, upload_image_to_telegram, initialize_telegram_client
from custom_utils import is_image, is_video, load_processed_files, save_processed_file, is_already_processed

# Numero massimo di upload contemporanei
MAX_CONCURRENT_UPLOADS = 3

async def handle_video(client, config, group_entity, file_path):
    """Gestisce il caricamento di un video su Telegram."""
    print(f"Video trovato: {file_path}")

    thumbnail_path = None
    caption = None

    if config["VIDEO_THUMBNAIL"]:
        thumbnail_path = extract_thumbnail(file_path)

    if config["VIDEO_CAPTION"]:
        caption = os.path.splitext(os.path.basename(file_path))[0]

    success = await upload_video_to_telegram(
        client=client,
        group_entity=group_entity,
        video_path=file_path,
        thumbnail_path=thumbnail_path,
        supports_streaming=config["SUPPORT_VIDEO_STREAMING"],
        show_progress=config["SHOW_PROGRESS_BAR"],
        caption=caption,
        reply_to_message_id=config["REPLY_ID"]
    )

    if thumbnail_path and os.path.isfile(thumbnail_path):
        os.remove(thumbnail_path)

    if config["DELETE_AFTER_UPLOAD"] and os.path.isfile(file_path) and success:
        os.remove(file_path)

    print("Caricamento video completato!" if success else "Caricamento fallito.")
    return success

async def handle_image(client, config, group_entity, file_path):
    """Gestisce il caricamento di un'immagine su Telegram."""
    print(f"Immagine trovata: {file_path}")

    caption = None
    if config["IMAGE_CAPTION"]:
        caption = os.path.splitext(os.path.basename(file_path))[0]

    success = await upload_image_to_telegram(
        client=client,
        group_entity=group_entity,
        image_path=file_path,
        show_progress=config["SHOW_PROGRESS_BAR"],
        caption=caption,
        reply_to_message_id=config["REPLY_ID"]
    )

    if config["DELETE_AFTER_UPLOAD"] and os.path.isfile(file_path) and success:
        os.remove(file_path)

    print("Caricamento immagine completato!" if success else "Caricamento fallito.")
    return success

async def process_file(client, config, group_entity, file_path, processed_set, semaphore):
    """Gestisce un file in base al tipo, se non è già stato processato."""
    async with semaphore:
        if is_already_processed(file_path, processed_set):
            print(f"Già processato, salto: {file_path}")
            return

        if is_video(file_path):
            success = await handle_video(client, config, group_entity, file_path)
            if success:
                save_processed_file(file_path, config["PROCESSED_FILES_PATH"], processed_set)

        elif is_image(file_path):
            success = await handle_image(client, config, group_entity, file_path)
            if success:
                save_processed_file(file_path, config["PROCESSED_FILES_PATH"], processed_set)

        else:
            print(f"Skippato (tipo non supportato): {file_path}")

async def process_folder(client, config, group_entity, folder, processed_set, semaphore):
    """Processa tutti i file all'interno della cartella con upload parallelo."""
    if not os.path.isdir(folder):
        print(f"Errore: la cartella {folder} non esiste.")
        return

    print(f"Controllando la cartella: {folder}")

    files = sorted(os.listdir(folder))

    tasks = []
    for file in files:
        full_path = os.path.join(folder, file)
        if os.path.isfile(full_path):
            tasks.append(process_file(client, config, group_entity, full_path, processed_set, semaphore))

    await asyncio.gather(*tasks)

async def main():
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

    config_path = args.config
    if not os.path.exists(config_path):
        print(f"Errore: Il file di configurazione '{config_path}' non esiste.")
        return

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    folders = config.get("FOLDERS", [])
    if not folders:
        print("Errore: nessuna cartella configurata.")
        return

    client = await initialize_telegram_client(
        config["BOT_TOKEN"],
        config["API_ID"],
        config["API_HASH"],
        session_file=args.session
    )

    # Risolvi l'entity del gruppo una sola volta
    group_entity = await client.get_entity(config["GROUP_LINK"])

    # Carica i file già processati in memoria (set)
    processed_set = load_processed_files(config["PROCESSED_FILES_PATH"])

    # Semaforo per limitare gli upload contemporanei
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_UPLOADS)

    for folder in folders:
        await process_folder(client, config, group_entity, folder, processed_set, semaphore)

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
