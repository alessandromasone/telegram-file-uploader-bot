# Utilizziamo un'immagine base di Python
FROM python:3.9-slim

# Installiamo FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Creiamo e settiamo la directory di lavoro
WORKDIR /app

# Creiamo un file vuoto chiamato processed_file.txt
RUN touch /app/processed_file.txt

# Copiamo i files necessari (requirements.txt, main.py, etc.) all'interno dell'immagine
COPY requirements.txt /app/requirements.txt

# Copiamo tutti i file .py nella directory di lavoro
COPY *.py /app/

# Creiamo una variabile d'ambiente per il comando da eseguire prima di creare l'ambiente virtuale
# La variabile contiene il nome di uno script shell (.sh) da eseguire, se presente
# Per esempio, passare "setup.sh"
ENV SCRIPTS_TO_RUN=""

# Se SCRIPTS_TO_RUN è definito e non vuoto, eseguiamo lo script
RUN bash /app/$SCRIPTS_TO_RUN || echo "Nessuno script da eseguire"

# Creiamo un ambiente virtuale per Python
RUN python -m venv /venv

# Attiviamo l'ambiente virtuale e installiamo le dipendenze
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Comando per eseguire lo script Python quando il container viene avviato
CMD ["/venv/bin/python", "main.py"]
