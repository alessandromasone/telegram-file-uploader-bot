import os
import time
import cv2
import tempfile
import ffmpeg
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from tqdm import tqdm

# Funzione per estrarre il frame centrale del video come immagine
def extract_thumbnail(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()

    if ret:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            thumbnail_path = tmp_file.name
            cv2.imwrite(thumbnail_path, frame)
            cap.release()
            return thumbnail_path
    else:
        cap.release()
        return None

# Funzione per estrarre i metadati del video
def extract_video_metadata(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        raise ValueError("Nessun stream video trovato")
    
    duration = float(video_stream['duration'])
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    
    return {
        'duration': int(duration),
        'width': width,
        'height': height
    }

# Funzione principale per caricare il video
async def upload_video(client, group_link, video_path, reply_to_message_id):
    """Carica un video su Telegram con anteprima e metadati usando il client esistente."""
    try:
        # Ottieni il gruppo dal link
        group_entity = await client.get_entity(group_link)

        if not os.path.exists(video_path):
            print(f"Errore: Il file {video_path} non esiste.")
            return False

        # Estrai la thumbnail
        thumbnail_path = extract_thumbnail(video_path)
        if not thumbnail_path:
            print("Errore: non è stato possibile estrarre la thumbnail.")
            return False

        # Estrai i metadati del video
        metadata = extract_video_metadata(video_path)

        try:
            file_size = os.path.getsize(video_path)

            def progress_callback(current, total):
                progress = current / total
                pbar.n = progress * total
                pbar.last_print_n = pbar.n
                pbar.update(0)

            with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
                # Carica il file e invia con la barra di progresso
                video_file = await client.upload_file(video_path, progress_callback=progress_callback)
                thumbnail_file = await client.upload_file(thumbnail_path)

                # Invia il video con la thumbnail e i metadati
                await client.send_file(
                    group_entity,
                    video_file,
                    caption=os.path.splitext(os.path.basename(video_path))[0],
                    thumb=thumbnail_file,
                    supports_streaming=True,
                    attributes=[
                        DocumentAttributeVideo(
                            duration=metadata['duration'],
                            w=metadata['width'],
                            h=metadata['height'],
                            supports_streaming=True
                        )
                    ],
                    progress_callback=progress_callback,
                    reply_to=reply_to_message_id  # Usa l'ID del messaggio a cui rispondere
                )

            # Rimuovi la thumbnail temporanea
            os.remove(thumbnail_path)

            # Se tutto è andato bene, restituisci True
            return True

        except Exception as e:
            print(f"Errore durante l'upload: {e}")
            return False

    except Exception as e:
        print(f"Errore durante la gestione del gruppo: {e}")
        return False
