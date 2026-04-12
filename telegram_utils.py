from typing import Optional, Any, List
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo, InputFileBig, InputFile
from telethon.tl.functions.upload import SaveBigFilePartRequest, SaveFilePartRequest
from video_utils import extract_video_metadata
import os
import asyncio
import hashlib

# Numero di connessioni TCP parallele verso il DC
PARALLEL_SENDERS = 5
# Numero di worker per l'upload parallelo dei chunk (distribuiti tra i sender)
PARALLEL_UPLOAD_WORKERS = 10


async def _create_sender_pool(client: TelegramClient, count: int) -> List:
    """Crea un pool di sender con connessioni TCP separate verso lo stesso DC."""
    dc_id = client.session.dc_id
    senders = []
    for _ in range(count):
        sender = await client._borrow_exported_sender(dc_id)
        senders.append(sender)
    return senders


async def _release_sender_pool(client: TelegramClient, senders: List) -> None:
    """Rilascia i sender al pool del client."""
    for sender in senders:
        await client._return_exported_sender(sender)


async def parallel_upload_file(client: TelegramClient, file_path: str, show_progress: bool = False) -> Any:
    """
    Carica un file su Telegram usando connessioni TCP multiple.
    I chunk vengono distribuiti tra N sender paralleli per vero parallelismo di rete.
    """
    file_size = os.path.getsize(file_path)
    part_size = 512 * 1024  # 512KB - massimo consentito
    total_parts = (file_size + part_size - 1) // part_size
    file_name = os.path.basename(file_path)

    # ID casuale per il file (signed 64-bit)
    file_id = int.from_bytes(os.urandom(8), byteorder='little', signed=True)

    # File > 10MB usano il protocollo BigFile
    is_big = file_size > 10 * 1024 * 1024
    hash_md5 = hashlib.md5() if not is_big else None

    # Leggi tutte le parti in memoria
    parts_data = []
    with open(file_path, 'rb') as f:
        for _ in range(total_parts):
            data = f.read(part_size)
            if hash_md5:
                hash_md5.update(data)
            parts_data.append(data)

    # Progress tracking
    uploaded_bytes = 0
    lock = asyncio.Lock()
    pbar = None

    if show_progress:
        from tqdm import tqdm
        pbar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Caricamento {file_name}")

    # Crea pool di sender con connessioni TCP separate
    senders = await _create_sender_pool(client, PARALLEL_SENDERS)
    semaphore = asyncio.Semaphore(PARALLEL_UPLOAD_WORKERS)

    async def upload_part(part_idx, data):
        nonlocal uploaded_bytes
        async with semaphore:
            # Round-robin: distribuisci i chunk tra i sender
            sender = senders[part_idx % len(senders)]
            if is_big:
                req = SaveBigFilePartRequest(file_id, part_idx, total_parts, data)
            else:
                req = SaveFilePartRequest(file_id, part_idx, data)
            await sender.send(req)

            if pbar:
                async with lock:
                    uploaded_bytes += len(data)
                    pbar.n = uploaded_bytes
                    pbar.last_print_n = pbar.n
                    pbar.update(0)

    try:
        # Invia tutti i chunk in parallelo distribuiti tra le connessioni
        await asyncio.gather(*[upload_part(i, data) for i, data in enumerate(parts_data)])
    finally:
        if pbar:
            pbar.close()
        # Rilascia i sender al pool
        await _release_sender_pool(client, senders)

    # Restituisci l'InputFile per Telethon
    if is_big:
        return InputFileBig(id=file_id, parts=total_parts, name=file_name)
    else:
        return InputFile(id=file_id, parts=total_parts, name=file_name, md5_checksum=hash_md5.hexdigest())


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

        # Upload parallelo del video con connessioni multiple
        video_file = await parallel_upload_file(client, video_path, show_progress)

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

        # Upload parallelo dell'immagine con connessioni multiple
        image_file = await parallel_upload_file(client, image_path, show_progress)

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

    # Verifica se cryptg è disponibile per encryption veloce
    try:
        import cryptg
        print("cryptg attivo: encryption AES accelerata (C)")
    except ImportError:
        print("ATTENZIONE: cryptg non disponibile, encryption AES in puro Python (più lento)")

    return client
