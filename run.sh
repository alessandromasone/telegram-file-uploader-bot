#!/bin/bash
# Questo script rimuove tutte le cartelle __pycache__ ricorsivamente

python3 main.py

find . -type d -name "__pycache__" -exec rm -rf {} +
rm session_name.*
