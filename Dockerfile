FROM alpine:3.19

# Installa python, pip, ffmpeg, cron e venv
RUN apk add --no-cache python3 py3-pip ffmpeg dcron procps python3-dev build-base

WORKDIR /app

# Crea virtual environment
RUN python3 -m venv /app/venv

# Aggiorna pip all'interno del venv
RUN /app/venv/bin/pip install --upgrade pip

# Copia requirements e installa nel venv
COPY requirements.txt ./
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copia tutto il progetto
COPY . .

# Variabili di ambiente
ENV CRON="" \
    CONFIG_FILE="config.yaml" \
    SESSION_FILE="session.session" \
    PATH="/app/venv/bin:$PATH"

# Volumi
VOLUME ["/app/video", "/app/images"]

# CMD che genera il crontab e lancia cron
CMD if [ -z "$CRON" ]; then \
        echo "@reboot python3 /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    else \
        echo "$CRON python3 /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    fi \
    && crond -f -l 2
