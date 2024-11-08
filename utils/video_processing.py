import ffmpeg
import os
import tempfile

def split_video(input_file, max_size_mb=2048):
    """Divide un video in parti di dimensione massima specificata, utilizzando file temporanei con nomi personalizzati."""
    max_size_bytes = max_size_mb * 1024**2  # Converti MB in byte
    base_name_without_ext = os.path.splitext(os.path.basename(input_file))[0]  # Nome del file senza estensione
    file_extension = os.path.splitext(input_file)[1]  # Estensione del file originale
    
    try:
        # Ottieni la durata e il bitrate del video
        probe = ffmpeg.probe(input_file)
        duration = float(probe['format']['duration'])
        avg_bitrate = float(probe['format']['bit_rate'])
        
        max_size_bits = max_size_bytes * 8  # Converti byte in bit
        max_part_duration = max_size_bits / avg_bitrate  # Durata massima di una parte in secondi
        
        start_time = 0
        part_number = 0
        parts = []

        while start_time < duration:
            end_time = min(start_time + max_part_duration, duration)
            part_number += 1
            part_name = f"{base_name_without_ext}_part{part_number}{file_extension}"
            
            # Crea il percorso per il file temporaneo senza stringhe casuali
            output_file = os.path.join(tempfile.gettempdir(), part_name)

            # Usa ffmpeg per dividere il video
            (
                ffmpeg
                .input(input_file, ss=start_time, to=end_time)
                .output(output_file, c='copy')
                .run(overwrite_output=True)
            )
            
            parts.append(output_file)  # Aggiungi il nome del file temporaneo alla lista
            
            start_time = end_time

        return parts
    except Exception as e:
        print(f"Errore durante la suddivisione del video: {e}")
        return []