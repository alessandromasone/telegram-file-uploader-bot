import os
from telethon import TelegramClient
from tqdm import tqdm

# Funzione per estrarre un'anteprima (thumbnail) per l'immagine
def extract_thumbnail(image_path):
    # In questo caso, non serve fare nulla in particolare per un'immagine
    # poiché si può utilizzare direttamente il file immagine come thumbnail
    return image_path

# Funzione principale per caricare l'immagine
async def upload_image(client, group_link, image_path, reply_to_message_id):
    """Carica un'immagine su Telegram con anteprima."""
    
    try:
        # Ottieni il gruppo dal link
        group_entity = await client.get_entity(group_link)

        if not os.path.exists(image_path):
            print(f"Errore: Il file {image_path} non esiste.")
            return False

        # Estrai la thumbnail (in questo caso è l'immagine stessa)
        thumbnail_path = extract_thumbnail(image_path)
        if not thumbnail_path:
            print("Errore: non è stato possibile estrarre la thumbnail.")
            return False

        try:
            file_size = os.path.getsize(image_path)

            def progress_callback(current, total):
                progress = current / total
                pbar.n = progress * total
                pbar.last_print_n = pbar.n
                pbar.update(0)

            with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
                # Carica l'immagine e invia con la barra di progresso
                image_file = await client.upload_file(image_path, progress_callback=progress_callback)
                thumbnail_file = await client.upload_file(thumbnail_path)

                # Invia l'immagine con la thumbnail
                await client.send_file(
                    group_entity,
                    image_file,
                    caption=os.path.splitext(os.path.basename(image_path))[0],
                    thumb=thumbnail_file,  # Usa l'immagine stessa come anteprima
                    progress_callback=progress_callback,
                    reply_to=reply_to_message_id  # Usa l'ID del messaggio a cui rispondere
                )

            # Se tutto è andato bene, restituisci True
            return True

        except Exception as e:
            print(f"Errore durante l'upload: {e}")
            return False

    except Exception as e:
        print(f"Errore durante la gestione del gruppo: {e}")
        return False
