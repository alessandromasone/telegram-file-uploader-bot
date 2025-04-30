# Telegram File Uploader Bot

Questo repository contiene un bot Telegram sviluppato in Python che consente di caricare automaticamente file (attualmente video e immagini) da cartelle locali a un gruppo o canale Telegram specificato.

## Funzionalità

* **Caricamento Automatico:** Monitora le cartelle configurate e carica i nuovi file.
* **Supporto Video e Immagini:** Gestisce il caricamento di file video (.mp4, .avi, .mov, .mkv, .webm) e immagini (.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp).
* **Gestione File Processati:** Tiene traccia dei file già caricati per evitare duplicati.
* **Thumbnail Video:** Opzione per estrarre e includere thumbnail per i video caricati.
* **Barra di Progresso:** Opzione per mostrare una barra di progresso durante il caricamento dei file.
* **Streaming Video:** Supporto opzionale per lo streaming video.
* **Didascalie Personalizzabili:** Opzione per includere il nome del file come didascalia per video e immagini.
* **Eliminazione Post-Caricamento:** Opzione per eliminare i file locali dopo un caricamento riuscito.

## Prerequisiti

* Python 3.x
* Account Telegram e accesso all'API di Telegram (ottenibile tramite BotFather e My Telegram API)
* Librerie Python richieste (`telethon`, `PyYAML`, `ffmpeg-python`, `opencv-python`, `tqdm`)
* FFmpeg installato sul sistema per l'estrazione dei metadati video e delle thumbnail.

## Installazione

1.  Clonare il repository:
    ```bash
    git clone https://github.com/alessandromasone/telegram-file-uploader-bot
    cd telegram-file-uploader-bot
    ```
2.  Installare le dipendenze Python (si consiglia l'uso di un ambiente virtuale):
    ```bash
    pip install -r requirements.txt
    ```
3.  Installare FFmpeg (fare riferimento alla documentazione ufficiale di FFmpeg per il proprio sistema operativo).

## Configurazione

1.  Rinominare `config.example.yaml` in `config.yaml`.
2.  Aprire `config.yaml` e compilare i seguenti campi con i propri dati:
    * `BOT_TOKEN`: Il token HTTP API ottenuto da BotFather.
    * `API_ID`: L'API ID ottenuto da My Telegram API.
    * `API_HASH`: L'API Hash ottenuto da My Telegram API.
    * `GROUP_LINK`: L'ID del gruppo o canale Telegram dove caricare i file (deve iniziare con `-100` per i privati).
    * `REPLY_ID`: (Opzionale) L'ID di un messaggio a cui rispondere. (Gruppo con thread)
    * `FOLDERS`: Una lista di percorsi alle cartelle da monitorare per i file da caricare.
    * `PROCESSED_FILES_PATH`: Il percorso di un file di testo dove verranno registrati i percorsi dei file già processati.
    * `VIDEO_THUMBNAIL`: `true` o `false` per abilitare/disabilitare le thumbnail dei video.
    * `SHOW_PROGRESS_BAR`: `true` o `false` per mostrare la barra di progresso.
    * `SUPPORT_VIDEO_STREAMING`: `true` o `false` per abilitare/disabilitare lo streaming video.
    * `VIDEO_CAPTION`: `true` o `false` per usare il nome del file video come didascalia.
    * `IMAGE_CAPTION`: `true` o `false` per usare il nome del file immagine come didascalia.
    * `DELETE_AFTER_UPLOAD`: `true` o `false` per eliminare i file locali dopo il caricamento.

## Esecuzione

Per avviare il bot, eseguire il file `main.py`:

```bash
python main.py
```

Il bot si connetterà a Telegram e inizierà a monitorare le cartelle specificate nel file `config.yaml`, caricando i file supportati che non sono ancora stati processati.

## Struttura del Progetto

* `main.py`: Punto di ingresso principale del bot. Gestisce la lettura della configurazione, l'inizializzazione del client Telegram e il processo di scansione e caricamento dei file.
* `config.example.yaml`: File di esempio per la configurazione del bot.
* `telegram_utils.py`: Contiene funzioni per l'interazione con l'API di Telegram, incluse le funzioni per il caricamento di video e immagini.
* `video_utils.py`: Contiene funzioni relative all'elaborazione video, come l'estrazione di metadati e thumbnail.
* `custom_utils.py`: Contiene utility personalizzate, come la verifica del tipo di file e la gestione dei file processati.

## Contribuire

Sentiti libero di contribuire al progetto aprendo issue o pull request.

## Licenza

Distribuito sotto la **GNU General Public License v3.0**. Vedi il file [LICENSE](LICENSE) per maggiori dettagli.