# Utilizziamo un'immagine base di Python
FROM python:3.12-slim

# Installiamo FFmpeg e puliamo la cache apt per ridurre la dimensione dell'immagine
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Creiamo e settiamo la directory di lavoro
WORKDIR /app

# Creiamo un file vuoto chiamato processed_file.txt
RUN touch /app/processed_file.txt

# Copiamo i files necessari (requirements.txt, main.py, etc.) all'interno dell'immagine
COPY requirements.txt /app/requirements.txt

# Creiamo un ambiente virtuale per Python e installiamo le dipendenze
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY *.py /app/
COPY config.example.yaml /app/config.example.yaml

# Settiamo variabili d'ambiente (puoi modificarle al momento del run)
ENV CONFIG_FILE="config.yaml"
ENV SESSION_FILE="/tmp/session.session"

# Comando per eseguire lo script Python
CMD sh -c 'if [ -f /app/run.sh ]; then /app/run.sh; fi; /venv/bin/python main.py --config "$CONFIG_FILE" --session "$SESSION_FILE"'
