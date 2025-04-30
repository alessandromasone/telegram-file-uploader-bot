import ffmpeg
import os
import cv2
import tempfile
from typing import Dict, Any

def extract_video_metadata(video_path: str) -> Dict[str, Any]:
    """Estrae metadati (durata, larghezza, altezza) dal video."""
    try:
        # Utilizza ffmpeg per ottenere informazioni sul video
        probe = ffmpeg.probe(video_path)
        
        # Trova lo stream video nel file (se presente)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

        if not video_stream:
            raise ValueError(f"Nessun stream video trovato in {video_path}")

        # Estrae durata, larghezza e altezza del video dallo stream
        duration = int(float(video_stream.get('duration', '0')))  # Durata in secondi
        width = int(video_stream.get('width', 0))  # Larghezza in pixel
        height = int(video_stream.get('height', 0))  # Altezza in pixel

        # Restituisce i metadati come un dizionario
        return {'duration': duration, 'width': width, 'height': height}

    except ffmpeg.Error as e:
        # Gestisce eventuali errori di ffmpeg durante l'estrazione dei metadati
        raise RuntimeError(f"Errore durante l'estrazione dei metadati con ffprobe: {e.stderr.decode()}")

# Funzione per estrarre il frame centrale del video come immagine (thumbnail)
def extract_thumbnail(video_path):
    """Estrae un frame centrale del video e lo salva come immagine JPEG."""
    # Apre il video con OpenCV
    cap = cv2.VideoCapture(video_path)
    
    # Ottiene il numero totale di frame nel video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calcola il frame centrale del video
    middle_frame = total_frames // 2
    
    # Imposta la posizione del video al frame centrale
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    
    # Legge il frame corrente
    ret, frame = cap.read()

    if ret:
        # Se il frame è stato letto correttamente, salva come immagine temporanea
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            thumbnail_path = tmp_file.name
            # Salva il frame come immagine JPEG
            cv2.imwrite(thumbnail_path, frame)
            cap.release()  # Rilascia la risorsa del video
            return thumbnail_path  # Restituisce il percorso dell'immagine
    else:
        # Se non è riuscito a leggere il frame, rilascia la risorsa e restituisce None
        cap.release()
        return None
