from typing import Optional, Any
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from video_utils import extract_video_metadata, extract_thumbnail
import os

# Funzione per caricare un video su Telegram con metadati e, se fornita, una thumbnail
async def upload_video_to_telegram(
    client: TelegramClient,
    group_link: str,
    video_path: str,
    thumbnail_path: Optional[str] = None,
    supports_streaming: bool = True,
    show_progress: bool = False,
    caption: Optional[str] = None,
    reply_to_message_id: Optional[int] = None
) -> bool:
    """Carica un video su Telegram con metadati e, se fornita, una thumbnail."""
    try:
        # Verifica la dimensione del video
        video_size = os.path.getsize(video_path)  # Ottiene la dimensione del file in byte
        max_video_size = 2 * 1024 * 1024 * 1024  # 2 GB in byte

        if video_size > max_video_size:
            print(f"Errore: Il file video '{video_path}' è troppo grande (>{2}GB).")
            return False  # Se il video è troppo grande, interrompe l'operazione

        # Ottieni i dettagli del gruppo tramite il link
        group_entity = await client.get_entity(group_link)

        if not os.path.exists(video_path):
            print(f"Errore: Il file video '{video_path}' non esiste.")
            return False  # Se il video non esiste, interrompe l'operazione

        # Estrae i metadati del video (durata, risoluzione, ecc.)
        try:
            metadata = extract_video_metadata(video_path)
        except Exception as e:
            print(f"Errore durante l'estrazione dei metadati: {e}")
            return False  # Se c'è un errore nell'estrazione dei metadati, interrompe l'operazione

        # Carica il video su Telegram (con la funzione che gestisce il progresso)
        video_file = await upload_file_with_progress(client, video_path, show_progress)

        thumbnail_file = None
        # Se è stata fornita una thumbnail, prova a caricarla
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumbnail_file = await client.upload_file(thumbnail_path)
        elif thumbnail_path:
            print(f"Attenzione: Il file thumbnail '{thumbnail_path}' non esiste. Proseguo senza.")

        # Prepara i parametri per l'invio del video
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

        # Aggiungi la thumbnail, se presente
        if thumbnail_file:
            send_file_kwargs["thumb"] = thumbnail_file

        # Aggiungi la didascalia, se presente
        if caption:
            send_file_kwargs["caption"] = caption

        # Invia il video
        await client.send_file(**send_file_kwargs)

        return True  # Se tutto è andato a buon fine, restituisci True

    except Exception as e:
        print(f"Errore durante l'upload del video: {e}")
        return False  # Se c'è un errore generico, restituisci False


# Funzione per caricare un'immagine su Telegram con anteprima (thumb)
async def upload_image_to_telegram(
    client: TelegramClient,
    group_link: str,
    image_path: str,
    show_progress: bool = False,
    caption: Optional[str] = None,
    reply_to_message_id: Optional[int] = None
) -> bool:
    """Carica un'immagine su Telegram con anteprima (thumb)."""
    try:
        # Ottieni i dettagli del gruppo tramite il link
        group_entity = await client.get_entity(group_link)

        if not os.path.exists(image_path):
            print(f"Errore: Il file '{image_path}' non esiste.")
            return False  # Se il file immagine non esiste, interrompe l'operazione

        try:
            # Carica l'immagine (con barra di progresso opzionale)
            image_file = await upload_file_with_progress(client, image_path, show_progress)
            thumbnail_file = await client.upload_file(image_path)

            # Prepara i parametri per l'invio dell'immagine
            send_file_kwargs = {
                "entity": group_entity,
                "file": image_file,
                "thumb": thumbnail_file,  # Imposta la thumbnail per l'immagine
                "reply_to": reply_to_message_id
            }
            
            # Aggiungi la didascalia, se presente
            if caption:
                send_file_kwargs["caption"] = caption

            # Invia l'immagine
            await client.send_file(**send_file_kwargs)

            return True  # Se tutto è andato a buon fine, restituisci True

        except Exception as e:
            print(f"Errore durante l'upload dell'immagine: {e}")
            return False  # Se c'è un errore durante il caricamento dell'immagine, restituisci False

    except Exception as e:
        print(f"Errore durante la gestione del gruppo: {e}")
        return False  # Se c'è un errore nell'ottenere il gruppo, restituisci False


# Funzione per caricare un file con una barra di progresso opzionale
async def upload_file_with_progress(client: TelegramClient, file_path: str, show_progress: bool) -> Any:
    """
    Carica un file su Telegram con una barra di progresso opzionale.
    """
    # Ottieni la dimensione del file
    file_size = os.path.getsize(file_path)
    
    if show_progress:
        # Se è richiesta la barra di progresso, usa tqdm per mostrarla
        from tqdm import tqdm
        def progress_callback(current: int, total: int):
            pbar.n = current
            pbar.last_print_n = pbar.n
            pbar.update(0)

        # Inizializza la barra di progresso
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Caricamento {os.path.basename(file_path)}") as pbar:
            return await client.upload_file(file_path, progress_callback=progress_callback)
    else:
        # Se non è richiesta la barra di progresso, carica direttamente il file
        return await client.upload_file(file_path)


# Funzione per inizializzare il client di Telegram con il bot token, api_id e api_hash
async def initialize_telegram_client(bot_token: str, api_id: str, api_hash: str) -> TelegramClient:
    """Avvia e restituisce un'istanza autenticata di TelegramClient."""
    session_file = 'session.session'  # Nome file usato da Telethon per la sessione
    use_existing_session = os.path.exists(session_file)

    # Crea un'istanza di TelegramClient
    client = TelegramClient('session', api_id, api_hash)

    if use_existing_session:
        print("Sessione esistente trovata. Riutilizzo...")
        await client.connect()  # Connetti il client
        if not await client.is_user_authorized():  # Verifica se l'utente è autorizzato
            print("Sessione non autorizzata. È richiesto un nuovo login.")
            await client.start(bot_token=bot_token) if bot_token else await client.start()
    else:
        print("Nessuna sessione trovata. Creazione nuova sessione...")
        await client.start(bot_token=bot_token) if bot_token else await client.start()

    return client  # Restituisce il client autenticato
