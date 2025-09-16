# Utilizziamo un'immagine base di Python
FROM python:3.9-slim

# Installiamo FFmpeg + dipendenze
RUN apt-get update && apt-get install -y \
    ffmpeg \
    vainfo \
    libva2 \
    libva-drm2 \
    libva-x11-2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Creiamo e settiamo la directory di lavoro
WORKDIR /app

# Creiamo un file vuoto chiamato processed_file.txt
RUN touch /app/processed_file.txt

# Copiamo i files necessari (requirements.txt, main.py, etc.) all'interno dell'immagine
COPY requirements.txt /app/requirements.txt
COPY *.py /app/
COPY config.example.yaml /app/config.example.yaml

# Creiamo un ambiente virtuale per Python
RUN python -m venv /venv

# Attiviamo l'ambiente virtuale e installiamo le dipendenze
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Settiamo variabili d'ambiente (puoi modificarle al momento del run)
ENV CONFIG_FILE="config.yaml"
ENV SESSION_FILE="/tmp/session.session"

# Comando per eseguire lo script Python
CMD sh -c 'if [ -f /app/run.sh ]; then /app/run.sh; fi; /venv/bin/python main.py --config "$CONFIG_FILE" --session "$SESSION_FILE"'
