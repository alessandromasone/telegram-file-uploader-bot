# Utilizziamo un'immagine base di Python
FROM python:3.9-slim

# Installiamo FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Creiamo e settiamo la directory di lavoro
WORKDIR /app

# Copiamo i files necessari (requirements.txt, main.py, etc.) all'interno dell'immagine
COPY requirements.txt /app/requirements.txt

# Copiamo tutti i file .py nella directory di lavoro
COPY *.py /app/

# Copiamo anche il file di configurazione esempio
COPY config.example.yaml /app/config.example.yaml

# Creiamo un ambiente virtuale per Python
RUN python -m venv /venv

# Attiviamo l'ambiente virtuale e installiamo le dipendenze
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Esponiamo la porta, se necessario
EXPOSE 5000

# Settiamo variabili d'ambiente (puoi modificarle al momento del run)
ENV CONFIG_FILE="config.yaml"
ENV SESSION_FILE="session.session"

# Comando per eseguire lo script Python, passando i parametri come variabili d'ambiente
CMD ["/venv/bin/python", "main.py", "--config", "$CONFIG_FILE", "--session", "$SESSION_FILE"]
