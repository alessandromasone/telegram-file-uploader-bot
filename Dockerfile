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
COPY main.py /app/main.py
COPY test.py /app/test.py

# Creiamo una variabile d'ambiente per i comandi da eseguire prima di creare l'ambiente virtuale
# La variabile contiene una lista di script separati da virgola
# Per esempio, passare `script1.sh,script2.py`
ENV SCRIPTS_TO_RUN=""

# Eseguiamo gli script definiti in SCRIPTS_TO_RUN prima di creare l'ambiente virtuale
RUN if [ -n "$SCRIPTS_TO_RUN" ]; then \
        IFS=',' read -ra SCRIPTS <<< "$SCRIPTS_TO_RUN"; \
        for script in "${SCRIPTS[@]}"; do \
            if [ -z "$script" ]; then \
                echo "Errore: uno degli script è vuoto."; \
                exit 1; \
            fi; \
            echo "Eseguendo lo script: $script"; \
            if [[ "$script" == *.sh ]]; then \
                bash /app/scripts/$script; \
            elif [[ "$script" == *.py ]]; then \
                /venv/bin/python /app/scripts/$script; \
            else \
                echo "Tipo di script non riconosciuto: $script"; \
            fi; \
        done; \
    else \
        echo "Nessuno script da eseguire."; \
    fi

# Creiamo un ambiente virtuale per Python
RUN python -m venv /venv

# Attiviamo l'ambiente virtuale e installiamo le dipendenze
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt

# Comando per eseguire lo script Python quando il container viene avviato
CMD ["/venv/bin/python", "main.py"]
