# Changelog

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)
e il progetto adotta il [Semantic Versioning](https://semver.org/lang/it/).

> Le versioni precedenti alla 1.0.0 sono state ricostruite a posteriori dalla
> storia dei commit e non hanno un tag git né un'immagine Docker dedicata.

## [Unreleased]

## [1.0.0] - 2026-11-25

Prima release versionata.

### Aggiunto
- `version.py` come unica fonte della versione dell'applicazione.
- Opzione `--version` da riga di comando e stampa della versione all'avvio.
- Variabile d'ambiente `APP_VERSION` (impostata dalla CI nelle immagini Docker).
- `CHANGELOG.md`.
- `.dockerignore` per evitare che credenziali, sessioni e file locali finiscano nel build context.
- Label OCI nell'immagine Docker (titolo, sorgente, licenza, versione).
- GitHub Action con:
  - build e push su GHCR per `main`, `develop` e tag `vX.Y.Z`;
  - tag Docker versionati (`X.Y.Z`, `X.Y`, `X`, `latest`, `develop`, `X.Y.Z-dev.N`, `sha-…`);
  - build di verifica (senza push) sulle pull request;
  - controllo che il tag git coincida con `version.py` e che il CHANGELOG contenga la versione;
  - controllo di sintassi Python e validazione di `config.example.yaml`;
  - creazione automatica della GitHub Release con le note prese dal CHANGELOG.
- Docstring di modulo in tutti i file Python.

### Modificato
- README riscritto: uso con Docker, variabili d'ambiente, branching, versioning e processo di release.
- `config.example.yaml`: valori di default validi e commentati.
- Il tag Docker `latest` ora indica l'ultima release (tag `vX.Y.Z`) e non più l'ultimo commit su `main`; per l'ultimo commit su `main` usare il tag `main`.

### Corretto
- `config.example.yaml` usava `true|false` come valore: YAML lo interpreta come stringa non vuota, quindi come *vero*. Copiando il file senza modificarlo si attivavano tutte le opzioni, compresa `DELETE_AFTER_UPLOAD`. Ora i valori sono booleani veri e `DELETE_AFTER_UPLOAD` è `false` di default.

## [0.6.0] - 2026-11-25

### Aggiunto
- Variabile d'ambiente `MATCH_BY_FILENAME` per scegliere se considerare processato un file con lo stesso nome in un'altra cartella.
- Variabile d'ambiente `MIN_FILE_AGE_SECONDS` per saltare i file modificati di recente (es. ancora in copia).

### Modificato
- Un upload è considerato riuscito solo se Telegram restituisce un messaggio contenente il media.

## [0.5.0] - 2026-04-12

### Aggiunto
- Upload parallelo dei chunk su più connessioni TCP verso lo stesso datacenter.
- Verifica della presenza di `cryptg` per la cifratura AES accelerata.

### Modificato
- Miglioramenti generali di velocità di upload e qualità del codice.
- Controllo della conferma di ogni chunk da parte di Telegram.

## [0.4.0] - 2025-09-17

### Modificato
- I file di ogni cartella vengono caricati in ordine alfabetico.
- Controllo dei file già processati più affidabile.

## [0.3.0] - 2025-09-06

### Aggiunto
- `Dockerfile` e pubblicazione dell'immagine su GHCR tramite GitHub Action.
- Hook opzionale `/app/run.sh` eseguito prima dell'avvio del bot nel container.

## [0.2.1] - 2025-08-17

### Corretto
- Disconnessione corretta del client Telegram a fine esecuzione.

### Modificato
- Dimensione dei chunk di upload dei video fissata a 512 KB.

## [0.2.0] - 2025-04-30

### Aggiunto
- Argomenti `--config` e `--session` da riga di comando.
- Riutilizzo del file di sessione Telethon tra un avvio e l'altro.

## [0.1.0] - 2024-11-08

### Aggiunto
- Prima versione: caricamento di video e immagini da cartelle locali verso un gruppo o canale Telegram.
- Thumbnail dei video, barra di avanzamento, didascalie, eliminazione dopo l'upload.
- Registro dei file già processati.

[Unreleased]: https://github.com/alessandromasone/telegram-file-uploader-bot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/alessandromasone/telegram-file-uploader-bot/releases/tag/v1.0.0
