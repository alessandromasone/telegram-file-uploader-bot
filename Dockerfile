FROM python:3.11-slim

# Installa ffmpeg, cron e strumenti di sistema
RUN apt-get update && apt-get install -y \
    ffmpeg cron procps build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crea virtual environment
RUN python -m venv /app/venv

# Aggiorna pip all'interno del venv
RUN /app/venv/bin/pip install --upgrade pip setuptools wheel

# Copia requirements e installa nel venv
COPY requirements.txt ./
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copia tutto il progetto
COPY . .

# Variabili di ambiente
ENV CRON="" \
    CONFIG_FILE="config.yaml" \
    SESSION_FILE="session.session" \
    PATH="/app/venv/bin:$PATH"  # aggiunge il venv al PATH

# Volumi per video, immagini e session
VOLUME ["/app/video", "/app/images", "/app/session"]

# CMD che genera il crontab dinamicamente e lancia cron
CMD if [ -z "$CRON" ]; then \
        echo "@reboot python /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    else \
        echo "$CRON python /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    fi \
    && cron -f
