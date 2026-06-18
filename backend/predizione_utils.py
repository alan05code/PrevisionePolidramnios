"""Funzioni di supporto per la previsione (estrazione) dal modello salvato.

Codice adattato dal notebook `previsione.ipynb`.
"""
from pathlib import Path

import joblib
import pandas as pd

from config import PercorsoModello


def CaricaModello(percorso: Path = PercorsoModello) -> dict:
    """Carica il pacchetto joblib salvato dal training (pipeline + metadati)."""
    percorso = Path(percorso)
    if not percorso.exists():
        raise FileNotFoundError(f"Modello non trovato: {percorso}. Esegui prima il training.")
    return joblib.load(percorso)


def PrevediPolidramnios(dati: dict, pacchetto: dict) -> dict:
    """Prevede il Polidramnios per una singola paziente.

    `dati` = dizionario con le feature (chiavi = nomi colonna).
    Ritorna {"previsione": 0/1, "probabilita": float}.
    """
    features = pacchetto["features"]
    mancanti = [c for c in features if c not in dati]
    if mancanti:
        raise ValueError(f"Dati mancanti: {mancanti}")

    # Una riga, colonne nell'ordine atteso dalla pipeline.
    X = pd.DataFrame([{c: dati[c] for c in features}])[features]
    prob = float(pacchetto["pipeline"].predict_proba(X)[0, 1])
    previsione = int(prob >= pacchetto["threshold"])
    return {"previsione": previsione, "probabilita": prob}