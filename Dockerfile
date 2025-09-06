FROM alpine:3.19

# Installa python, pip, ffmpeg, cron
RUN apk add --no-cache python3 py3-pip ffmpeg dcron procps

WORKDIR /app

# Copia requirements se ci sono
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia il progetto
COPY . .

# Variabili di ambiente
ENV CRON="" \
    CONFIG_FILE="config.yaml" \
    SESSION_FILE="session.session"

# Volumi per video, immagini e session
VOLUME ["/app/video", "/app/images"]

# CMD che genera il crontab dinamicamente e lancia cron
CMD if [ -z "$CRON" ]; then \
        echo "@reboot python3 /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    else \
        echo "$CRON python3 /app/main.py --config $CONFIG_FILE --session $SESSION_FILE" > /etc/crontabs/root ; \
    fi \
    && crond -f -l 2
