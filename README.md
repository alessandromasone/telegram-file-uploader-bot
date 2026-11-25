# Telegram File Uploader Bot

[![Docker image](https://github.com/alessandromasone/telegram-file-uploader-bot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/alessandromasone/telegram-file-uploader-bot/actions/workflows/docker-image.yml)
[![Release](https://img.shields.io/github/v/release/alessandromasone/telegram-file-uploader-bot)](https://github.com/alessandromasone/telegram-file-uploader-bot/releases)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Bot Telegram in Python che carica automaticamente video e immagini da cartelle locali in un gruppo o canale Telegram.

## Indice

- [Funzionalità](#funzionalità)
- [Come funziona](#come-funziona)
- [Prerequisiti](#prerequisiti)
- [Installazione locale](#installazione-locale)
- [Configurazione](#configurazione)
- [Esecuzione](#esecuzione)
- [Docker](#docker)
- [Struttura del progetto](#struttura-del-progetto)
- [Limitazioni note](#limitazioni-note)
- [Branching, versioning e release](#branching-versioning-e-release)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

## Funzionalità

- **Caricamento automatico** dei file presenti nelle cartelle configurate.
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` (fino a 2 GB), con durata e risoluzione lette tramite FFmpeg.
- **Immagini**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`.
- **Niente duplicati**: i file caricati vengono registrati e saltati alle esecuzioni successive.
- **Upload veloce**: chunk inviati in parallelo su più connessioni TCP, cifratura accelerata con `cryptg`.
- **Thumbnail video** estratta dal frame centrale (opzionale).
- **Barra di avanzamento** durante l'upload (opzionale).
- **Streaming video** (opzionale).
- **Didascalie** con il nome del file (opzionali, separate per video e immagini).
- **Eliminazione dopo l'upload** dei file locali (opzionale).
- **Risposta a un messaggio/topic** nei gruppi con thread.

## Come funziona

A ogni avvio il bot:

1. legge `config.yaml` e si autentica su Telegram (riutilizzando il file di sessione, se presente);
2. scansiona ogni cartella in `FOLDERS` (solo il primo livello, in ordine alfabetico);
3. per ogni file supportato non ancora presente nel registro `PROCESSED_FILES_PATH`, lo carica e, se l'upload va a buon fine, lo aggiunge al registro;
4. si disconnette e termina.

L'esecuzione è **one-shot**: il bot non resta in ascolto. Per caricare periodicamente i nuovi file va avviato da uno scheduler (cron, timer systemd, Task Scheduler di Windows, ecc.). Vedi gli esempi in [Esecuzione](#esecuzione) e [Docker](#docker).

## Prerequisiti

- Python 3.10 o superiore (l'immagine Docker usa Python 3.12).
- [FFmpeg](https://ffmpeg.org/download.html) installato e disponibile nel `PATH` (serve `ffprobe`).
- Un bot Telegram creato con [@BotFather](https://t.me/BotFather) e aggiunto al gruppo/canale di destinazione con il permesso di inviare messaggi e media.
- `API_ID` e `API_HASH` ottenuti da [my.telegram.org](https://my.telegram.org) → *API development tools*.

## Installazione locale

```bash
git clone https://github.com/alessandromasone/telegram-file-uploader-bot
cd telegram-file-uploader-bot

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Dipendenze Python principali: `telethon`, `cryptg`, `PyYAML`, `ffmpeg-python`, `opencv-python-headless`, `tqdm`.

## Configurazione

Copia il file di esempio e modificalo:

```bash
cp config.example.yaml config.yaml
```

| Chiave | Tipo | Descrizione |
|---|---|---|
| `BOT_TOKEN` | stringa | Token del bot fornito da @BotFather. |
| `API_ID` | stringa/numero | API ID da my.telegram.org. |
| `API_HASH` | stringa | API hash da my.telegram.org. |
| `GROUP_LINK` | numero | ID del gruppo/canale di destinazione. Supergruppi e canali iniziano con `-100`. |
| `REPLY_ID` | numero o `null` | ID del messaggio/topic a cui rispondere (gruppi con thread). `null` per nessuno. |
| `FOLDERS` | lista | Cartelle da scansionare (non ricorsivo). |
| `PROCESSED_FILES_PATH` | stringa | File di testo con l'elenco dei file già caricati. |
| `VIDEO_THUMBNAIL` | bool | Estrae e allega una thumbnail ai video. |
| `SHOW_PROGRESS_BAR` | bool | Mostra la barra di avanzamento. |
| `SUPPORT_VIDEO_STREAMING` | bool | Marca i video come riproducibili in streaming. |
| `VIDEO_CAPTION` | bool | Usa il nome del file come didascalia dei video. |
| `IMAGE_CAPTION` | bool | Usa il nome del file come didascalia delle immagini. |
| `DELETE_AFTER_UPLOAD` | bool | **Elimina il file locale** dopo un upload riuscito. |

> **Attenzione:** le opzioni booleane vanno scritte come `true` o `false` senza virgolette. Qualsiasi altra stringa (ad esempio `"false"` tra virgolette o `true|false`) viene interpretata come *vera*.

### Variabili d'ambiente

| Variabile | Default | Descrizione |
|---|---|---|
| `MATCH_BY_FILENAME` | `true` | Se `true`, un file è considerato già caricato anche se nel registro c'è un file con lo **stesso nome** in un'altra cartella. Con `false` si confronta solo il percorso completo. |
| `MIN_FILE_AGE_SECONDS` | `0` | Salta i file modificati negli ultimi N secondi, utile se i file vengono copiati mentre il bot gira. `0` disattiva il controllo. |
| `APP_VERSION` | — | Versione mostrata all'avvio. Impostata automaticamente nelle immagini Docker; in locale si usa quella di `version.py`. |
| `CONFIG_FILE` | `config.yaml` | Solo Docker: percorso del file di configurazione. |
| `SESSION_FILE` | `/tmp/session.session` | Solo Docker: percorso del file di sessione Telethon. |

## Esecuzione

```bash
python main.py                                  # usa config.yaml e session.session
python main.py --config /percorso/config.yaml --session /percorso/bot.session
python main.py --version
```

Al primo avvio viene creato il file di sessione; dalle esecuzioni successive viene riutilizzato.

Esempio di esecuzione ogni 10 minuti con cron:

```cron
*/10 * * * * cd /opt/telegram-file-uploader-bot && .venv/bin/python main.py >> uploader.log 2>&1
```

## Docker

L'immagine è pubblicata su GitHub Container Registry:

```bash
docker pull ghcr.io/alessandromasone/telegram-file-uploader-bot:latest
```

### Tag disponibili

| Tag | Contenuto | Consigliato per |
|---|---|---|
| `X.Y.Z` (es. `1.0.0`) | Release specifica, immutabile | Produzione |
| `X.Y` (es. `1.0`) | Ultima patch della minor `X.Y` | Produzione con fix automatici |
| `X` (es. `1`) | Ultima release della major `X` | |
| `latest` | Ultima release pubblicata | Prove rapide |
| `main` | Ultimo commit su `main` | |
| `develop` | Ultimo commit su `develop` | Test di funzionalità in arrivo |
| `X.Y.Z-dev.N` | Build N di `develop` | Test di una build precisa |
| `sha-<commit>` | Commit specifico | Debug |

### Esempio

Struttura consigliata:

```
uploader/
├── config.yaml
└── data/           # sessione e registro dei file processati (persistenti)
```

Nel `config.yaml` usa i percorsi **del container**:

```yaml
FOLDERS:
  - "/media/video"
  - "/media/foto"
PROCESSED_FILES_PATH: "/data/processed_files.txt"
```

Avvio:

```bash
docker run --rm \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -v "$(pwd)/data:/data" \
  -v /percorso/video:/media/video \
  -v /percorso/foto:/media/foto \
  -e SESSION_FILE=/data/bot.session \
  -e MIN_FILE_AGE_SECONDS=60 \
  ghcr.io/alessandromasone/telegram-file-uploader-bot:1.0.0
```

> Monta sempre `/data` (o un'altra cartella persistente) per sessione e registro: con il default `SESSION_FILE=/tmp/session.session` la sessione si perde a ogni nuovo container, e senza un registro persistente i file verrebbero ricaricati.

Poiché il bot termina a fine scansione, per l'esecuzione periodica pianifica il `docker run` con cron o con lo scheduler del tuo NAS. Se è presente `/app/run.sh` (montato come volume ed eseguibile), viene eseguito prima del bot.

### Build locale

```bash
docker build --build-arg APP_VERSION=1.0.0-local -t telegram-file-uploader-bot .
```

## Struttura del progetto

```
.
├── main.py               # Entry point: argomenti, config, scansione cartelle, gestione video/immagini
├── telegram_utils.py     # Client Telethon, upload parallelo, invio video e immagini
├── video_utils.py        # Metadati (ffprobe) e thumbnail (OpenCV)
├── custom_utils.py       # Tipi di file, registro dei file processati, controllo età file
├── version.py            # Versione dell'applicazione
├── config.example.yaml   # Configurazione di esempio
├── requirements.txt
├── Dockerfile
├── CHANGELOG.md
└── .github/workflows/
    └── docker-image.yml  # CI: controlli, build/push immagine, GitHub Release
```

## Limitazioni note

- La scansione delle cartelle **non è ricorsiva**: le sottocartelle vengono ignorate.
- I video oltre **2 GB** vengono saltati (limite dei bot Telegram).
- Ogni file viene **letto interamente in memoria** prima dell'upload: servono almeno tanti byte di RAM quanto il file più grande.
- Con `MATCH_BY_FILENAME=true` (default) due file diversi con lo stesso nome in cartelle diverse sono considerati lo stesso file.

## Branching, versioning e release

Il progetto usa il [Semantic Versioning](https://semver.org/lang/it/) (`MAJOR.MINOR.PATCH`) e il formato [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/).

| Branch / ref | Scopo | Immagine Docker |
|---|---|---|
| `develop` | Sviluppo corrente, dove si integrano le nuove funzionalità | `develop`, `X.Y.Z-dev.N` |
| `main` | Codice stabile, pronto per la release | `main` |
| tag `vX.Y.Z` | Release | `X.Y.Z`, `X.Y`, `X`, `latest` |
| branch di feature | Si apre una PR verso `develop` | nessuna (solo build di verifica) |

La versione si trova in un solo punto: `__version__` in [`version.py`](version.py).

### Come fare una release

1. Su `develop`, aggiorna `__version__` in `version.py` (es. `1.1.0`).
2. In `CHANGELOG.md` sposta le voci da `[Unreleased]` in una nuova sezione `## [1.1.0] - AAAA-MM-GG` e aggiorna i link di confronto in fondo al file.
3. Fai il merge di `develop` in `main`.
4. Crea e pubblica il tag su `main`:
   ```bash
   git checkout main && git pull
   git tag -a v1.1.0 -m "v1.1.0"
   git push origin v1.1.0
   ```
5. La GitHub Action verifica che tag, `version.py` e CHANGELOG coincidano, pubblica l'immagine con i tag di versione e crea la GitHub Release con le note del CHANGELOG.

Quale numero aumentare:

- **PATCH** (`1.0.1`): bugfix compatibili.
- **MINOR** (`1.1.0`): nuove funzionalità compatibili (nuove opzioni con default che non cambiano il comportamento).
- **MAJOR** (`2.0.0`): modifiche incompatibili (chiavi di configurazione rinominate o rimosse, comportamento di default cambiato).

## Contribuire

Issue e pull request sono benvenute. Apri le PR verso il branch `develop` e aggiungi una voce in `CHANGELOG.md` sotto `[Unreleased]`.

## Licenza

Distribuito sotto la **GNU General Public License v3.0**. Vedi il file [LICENSE](LICENSE).
