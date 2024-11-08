# Telegram File Uploader Bot

Questo progetto Python è un bot per Telegram che permette di caricare video e immagini su un gruppo Telegram. Utilizza la libreria `Telethon` per interagire con l'API di Telegram e supporta vari formati di file video e immagine. Il bot può caricare automaticamente i file da cartelle specificate, assicurandosi che vengano processati solo i file che non sono già stati caricati.

## Caratteristiche
- Carica file supportati (video e immagini) su un gruppo Telegram.
- Supporta vari formati video come `.mp4`, `.mkv`, `.avi` e altri.
- Supporta vari formati immagine come `.jpg`, `.jpeg`, `.png` e altri.
- Controlla automaticamente se un file è già stato caricato prima di procedere con il caricamento.
- Configurazione del bot tramite file JSON.
- Elaborazione asincrona dei file per un caricamento efficiente.

## Prerequisiti

Prima di eseguire il bot, assicurati di avere i seguenti prerequisiti:
- **Python 3.6+**
- **Telethon**: La libreria Python per interagire con l'API di Telegram.
- **ffmpeg**: Necessario per suddividere video di grandi dimensioni in parti più piccole.
- **PyQt5**: Per l'interfaccia grafica (GUI) per configurare il bot.

### Installazione

1. **Clona il repository**:
    ```bash
    git clone https://github.com/alessandromasone/telegram-file-uploader-bot.git
    cd telegram-file-uploader-bot
    ```

2. **Crea un ambiente virtuale**:
    ```bash
    python3 -m venv env
    source env/bin/activate  # Su Windows usa 'env\Scripts\activate'
    ```

3. **Installa le dipendenze**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Assicurati che `ffmpeg` sia installato**:
    - **Linux**: 
        ```bash
        sudo apt install ffmpeg
        ```
    - **MacOS**: 
        ```bash
        brew install ffmpeg
        ```
    - **Windows**: Scarica, installa e aggiungi alla variabili d'ambiente [FFmpeg](https://ffmpeg.org/download.html).

### Configurazione

Crea un file `config.json` nella directory principale con la seguente struttura (è presente un `config.template.json`):

```json
{
    "api_id": "TUO_API_ID",
    "api_hash": "TUO_API_HASH",
    "bot_token": "TUO_BOT_TOKEN",
    "group_link": -1001234567890,
    "thread_id": 1,
    "folders": [
        "media/video",
        "media/image"
    ]
}
```

- **api_id**: Il tuo ID API di Telegram (puoi ottenerlo su [my.telegram.org](https://my.telegram.org)).
- **api_hash**: Il tuo Hash API di Telegram (puoi ottenerlo su [my.telegram.org](https://my.telegram.org)).
- **bot_token**: Il token per il tuo bot di Telegram (puoi ottenerlo su [BotFather](https://core.telegram.org/bots#botfather)).
- **group_link**: L'ID univoco del gruppo Telegram in cui verranno caricati i file (ad esempio `-1001234567890`).
- **thread_id**: L'ID del thread per inviare i messaggi in thread specifici (opzionale).
- **folders**: Una lista di cartelle da monitorare per i file video e immagine.

### Utilizzo

1. **Avvia la GUI per la configurazione** (opzionale):
    Se desideri configurare facilmente il bot, puoi eseguire il programma grafico che ti permette di impostare i parametri del bot:

    ```bash
    python gui.py
    ```

    Si aprirà una semplice interfaccia grafica in cui puoi inserire i dettagli di configurazione del bot (API ID, API Hash, Bot Token, ecc.).

2. **Esegui lo script principale del bot**:
    Dopo aver configurato il bot, puoi avviarlo eseguendo il file `main.py`:

    ```bash
    python main.py
    ```

    Il bot esaminerà le cartelle specificate in `config.json` e caricherà i file video e immagine supportati nel gruppo Telegram indicato.

### Gestione dei file

- **File Video**: Se un video supera la dimensione massima consentita per il caricamento su Telegram, verrà automaticamente suddiviso in parti più piccole utilizzando `ffmpeg`.
- **File Immagine**: Le immagini vengono caricate direttamente con un'anteprima.

### Gestione degli errori
- Se un file è già stato caricato, verrà saltato per evitare duplicati.
- Se si verifica un errore durante il caricamento di un file, il bot mostrerà un messaggio di errore appropriato.

### Note aggiuntive

- **Limiti di Telegram**: Telegram impone dei limiti sulla dimensione dei file che possono essere caricati. Il bot gestisce automaticamente i video che superano la dimensione massima, suddividendoli in più parti.
- **Personalizzazione**: Le funzionalità del bot possono essere facilmente estese. Puoi modificare o aggiungere nuove funzionalità aggiornando le funzioni come `upload_file`, `split_video` o altre funzioni utilitarie.

## Contributi

Se desideri contribuire a questo progetto, sentiti libero di aprire un **issue** o inviare una **pull request**.

## Licenza

Distribuito sotto la **GNU General Public License v3.0**. Vedi il file [LICENSE](LICENSE) per maggiori dettagli.