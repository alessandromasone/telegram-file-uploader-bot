from typing import Optional, Any
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from video_utils import extract_video_metadata
import os

async def upload_video_to_telegram(
    client: TelegramClient,
    group_entity,
    video_path: str,
    thumbnail_path: Optional[str] = None,
    supports_streaming: bool = True,
    show_progress: bool = False,
    caption: Optional[str] = None,
    reply_to_message_id: Optional[int] = None
) -> bool:
    """Carica un video su Telegram con metadati e, se fornita, una thumbnail."""
    try:
        video_size = os.path.getsize(video_path)
        max_video_size = 2 * 1024 * 1024 * 1024  # 2 GB

        if video_size > max_video_size:
            print(f"Errore: Il file video '{video_path}' è troppo grande (>2GB).")
            return False

        if not os.path.exists(video_path):
            print(f"Errore: Il file video '{video_path}' non esiste.")
            return False

        try:
            metadata = extract_video_metadata(video_path)
        except Exception as e:
            print(f"Errore durante l'estrazione dei metadati: {e}")
            return False

        video_file = await upload_file_with_progress(client, video_path, show_progress)

        thumbnail_file = None
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_file = await client.upload_file(thumbnail_path)
        elif thumbnail_path:
            print(f"Attenzione: Il file thumbnail '{thumbnail_path}' non esiste. Proseguo senza.")

        send_file_kwargs = {
            "entity": group_entity,
            "file": video_file,
            "supports_streaming": supports_streaming,
            "attributes": [DocumentAttributeVideo(
                duration=metadata['duration'],
                w=metadata['width'],
                h=metadata['height'],
                supports_streaming=supports_streaming
            )],
            "reply_to": reply_to_message_id
        }

        if thumbnail_file:
            send_file_kwargs["thumb"] = thumbnail_file

        if caption:
            send_file_kwargs["caption"] = caption

        await client.send_file(**send_file_kwargs)
        return True

    except Exception as e:
        print(f"Errore durante l'upload del video: {e}")
        return False


async def upload_image_to_telegram(
    client: TelegramClient,
    group_entity,
    image_path: str,
    show_progress: bool = False,
    caption: Optional[str] = None,
    reply_to_message_id: Optional[int] = None
) -> bool:
    """Carica un'immagine su Telegram."""
    try:
        if not os.path.exists(image_path):
            print(f"Errore: Il file '{image_path}' non esiste.")
            return False

        image_file = await upload_file_with_progress(client, image_path, show_progress)

        send_file_kwargs = {
            "entity": group_entity,
            "file": image_file,
            "reply_to": reply_to_message_id
        }

        if caption:
            send_file_kwargs["caption"] = caption

        await client.send_file(**send_file_kwargs)
        return True

    except Exception as e:
        print(f"Errore durante l'upload dell'immagine: {e}")
        return False


async def upload_file_with_progress(client: TelegramClient, file_path: str, show_progress: bool) -> Any:
    """Carica un file su Telegram con una barra di progresso opzionale."""
    file_size = os.path.getsize(file_path)

    if show_progress:
        from tqdm import tqdm
        def progress_callback(current: int, total: int):
            pbar.n = current
            pbar.last_print_n = pbar.n
            pbar.update(0)

        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Caricamento {os.path.basename(file_path)}") as pbar:
            return await client.upload_file(file_path, progress_callback=progress_callback, part_size_kb=512)
    else:
        return await client.upload_file(file_path, part_size_kb=512)


async def initialize_telegram_client(
    bot_token: str,
    api_id: str,
    api_hash: str,
    session_file: str = 'session.session'
) -> TelegramClient:
    """Avvia e restituisce un'istanza autenticata di TelegramClient."""
    use_existing_session = os.path.exists(session_file)

    session_name = os.path.splitext(session_file)[0]
    client = TelegramClient(session_name, api_id, api_hash)

    if use_existing_session:
        print("Sessione esistente trovata. Riutilizzo...")
        await client.connect()
        if not await client.is_user_authorized():
            print("Sessione non autorizzata. È richiesto un nuovo login.")
            await client.start(bot_token=bot_token) if bot_token else await client.start()
    else:
        print("Nessuna sessione trovata. Creazione nuova sessione...")
        await client.start(bot_token=bot_token) if bot_token else await client.start()

    return client
