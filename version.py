"""Versione dell'applicazione.

Unica fonte di verità per il numero di versione (Semantic Versioning).
Quando si prepara una release aggiornare ``__version__`` e ``CHANGELOG.md``,
poi creare il tag ``vX.Y.Z`` sul branch ``main``: la GitHub Action verifica
che tag e ``__version__`` coincidano prima di pubblicare l'immagine Docker.
"""

import os

__version__ = "1.0.0"


def get_version() -> str:
    """Restituisce la versione in esecuzione.

    Nelle immagini Docker la CI imposta ``APP_VERSION`` (es. ``1.0.0`` per una
    release o ``1.0.0-dev.42`` per una build di ``develop``); in locale si
    ricade su ``__version__``.
    """
    return os.environ.get("APP_VERSION") or __version__
