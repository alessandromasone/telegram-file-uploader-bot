# Immagine base Python
FROM python:3.12-slim

# Versione dell'app, passata dalla CI (es. 1.0.0 o 1.0.0-dev.42).
# Se vuota, l'app usa __version__ definita in version.py.
ARG APP_VERSION=""

# Metadati OCI (la CI li sovrascrive/integra con docker/metadata-action)
LABEL org.opencontainers.image.title="telegram-file-uploader-bot" \
      org.opencontainers.image.description="Bot Telegram che carica video e immagini da cartelle locali in un gruppo o canale" \
      org.opencontainers.image.source="https://github.com/alessandromasone/telegram-file-uploader-bot" \
      org.opencontainers.image.licenses="GPL-3.0" \
      org.opencontainers.image.version="${APP_VERSION}"

# FFmpeg serve per metadati e thumbnail; puliamo la cache apt per ridurre la dimensione
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# File di registro vuoto di default (in produzione conviene puntare
# PROCESSED_FILES_PATH a un volume persistente, es. /data/processed_files.txt)
RUN touch /app/processed_file.txt

# Dipendenze in un virtualenv (layer separato per sfruttare la cache)
COPY requirements.txt /app/requirements.txt
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Codice sorgente
COPY *.py /app/
COPY config.example.yaml /app/config.example.yaml

# Variabili d'ambiente modificabili con `docker run -e ...`
#   CONFIG_FILE           percorso del config YAML
#   SESSION_FILE          file di sessione Telethon (montalo su un volume per riutilizzarlo)
#   APP_VERSION           versione mostrata all'avvio
#   MATCH_BY_FILENAME     true/false, vedi README
#   MIN_FILE_AGE_SECONDS  secondi minimi dall'ultima modifica, vedi README
ENV CONFIG_FILE="config.yaml" \
    SESSION_FILE="/tmp/session.session" \
    APP_VERSION="${APP_VERSION}" \
    PYTHONUNBUFFERED=1

# Se esiste /app/run.sh (montato come volume) viene eseguito prima del bot,
# utile per comandi di preparazione personalizzati.
CMD sh -c 'if [ -f /app/run.sh ]; then /app/run.sh; fi; /venv/bin/python main.py --config "$CONFIG_FILE" --session "$SESSION_FILE"'
