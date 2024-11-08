from PyQt5 import QtWidgets
import json
import subprocess
import sys
import os

# Funzione per caricare la configurazione da un file JSON
def carica_configurazione():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        # Configurazione di default
        return {
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

# Funzione per salvare la configurazione
def salva_configurazione():
    config["api_id"] = api_id_entry.text()
    config["api_hash"] = api_hash_entry.text()
    config["bot_token"] = bot_token_entry.text()
    config["group_link"] = int(group_link_entry.text())
    config["thread_id"] = int(thread_id_entry.text())
    config["folders"] = folders_entry.text().split(",")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    QtWidgets.QMessageBox.information(window, "Successo", "Configurazione salvata con successo!")

# Funzione per avviare un file Python esterno
def avvia_script():
    salva_configurazione()
    try:
        subprocess.Popen(["python", "main.py"])
        QtWidgets.QMessageBox.information(window, "Avvio", "Script avviato con successo!")
    except Exception as e:
        QtWidgets.QMessageBox.critical(window, "Errore", f"Errore nell'avviare lo script:\n{e}")

# Caricamento della configurazione (dal file o valori di default)
config = carica_configurazione()

# Creazione dell'interfaccia
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Configurazione Bot")
window.setGeometry(100, 100, 400, 400)
layout = QtWidgets.QVBoxLayout()

# Campi di input
api_id_entry = QtWidgets.QLineEdit(config["api_id"])
layout.addWidget(QtWidgets.QLabel("API ID"))
layout.addWidget(api_id_entry)

api_hash_entry = QtWidgets.QLineEdit(config["api_hash"])
layout.addWidget(QtWidgets.QLabel("API Hash"))
layout.addWidget(api_hash_entry)

bot_token_entry = QtWidgets.QLineEdit(config["bot_token"])
layout.addWidget(QtWidgets.QLabel("Bot Token"))
layout.addWidget(bot_token_entry)

group_link_entry = QtWidgets.QLineEdit(str(config["group_link"]))
layout.addWidget(QtWidgets.QLabel("Group Link"))
layout.addWidget(group_link_entry)

thread_id_entry = QtWidgets.QLineEdit(str(config["thread_id"]))
layout.addWidget(QtWidgets.QLabel("Thread ID"))
layout.addWidget(thread_id_entry)

folders_entry = QtWidgets.QLineEdit(",".join(config["folders"]))
layout.addWidget(QtWidgets.QLabel("Folders (comma-separated)"))
layout.addWidget(folders_entry)

# Pulsanti per salvare e avviare
salva_button = QtWidgets.QPushButton("Salva Configurazione")
salva_button.clicked.connect(salva_configurazione)
layout.addWidget(salva_button)

avvia_button = QtWidgets.QPushButton("Avvia Script")
avvia_button.clicked.connect(avvia_script)
layout.addWidget(avvia_button)

window.setLayout(layout)
window.show()
sys.exit(app.exec_())
