FROM python:3.11-slim

# Installa ffmpeg e strumenti di sistema
RUN apt-get update && apt-get install -y \
    ffmpeg build-essential bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crea virtual environment
RUN python -m venv /app/venv

# Aggiorna pip all'interno del venv
RUN bash -c "source /app/venv/bin/activate && pip install --upgrade pip setuptools wheel"

# Copia requirements e installa nel venv
COPY requirements.txt ./
RUN bash -c "source /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt"

# Copia tutto il progetto
COPY . .

# Variabili di ambiente
ENV CONFIG_FILE="config.yaml" \
    SESSION_FILE="session.session" \
    PATH="/app/venv/bin:$PATH"

# Volumi per video, immagini e session
VOLUME ["/app/video", "/app/images", "/app/session"]

# CMD: esegue il bot una sola volta all'avvio
CMD [ "bash", "-c", "source /app/venv/bin/activate && python /app/main.py --config \"$CONFIG_FILE\" --session \"$SESSION_FILE\"" ]
