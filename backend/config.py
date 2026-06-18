"""Configurazione del backend: percorsi e costanti delle colonne.

I percorsi sono relativi alla root del progetto (la cartella che contiene
`backend/`, `models/` e il dataset), così funzionano indipendentemente da dove
viene lanciato lo script.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PercorsoDati = ROOT / "dataset" / "dataset_polidramnios_10k.csv"
PercorsoModello = ROOT / "models" / "modello_polidramnios.joblib"

# Target e feature (l'ordine delle feature conta: deve combaciare con l'input del modello).
ColonnaTarget = "Polidramnios"
ColonneFeatures = [
    "Eta_anni",
    "Numero_Gravidanze_Pregresse",
    "Numero_Tagli_Cesarei_Pregressi",
    "Pressione_Diastolica_mmHg",
    "Insulina_Sierica_2ore",
    "Indice_Massa_Corporea",
    "Diabete_Gestazionale",
    "Diabete_Pregravidico",
]

# Continue = scalate; binarie = solo imputate; clipping = solo su queste 4.
ColonneContinue = [
    "Eta_anni",
    "Numero_Gravidanze_Pregresse",
    "Numero_Tagli_Cesarei_Pregressi",
    "Pressione_Diastolica_mmHg",
    "Insulina_Sierica_2ore",
    "Indice_Massa_Corporea",
]
ColonneBinarie = ["Diabete_Gestazionale", "Diabete_Pregravidico"]
ColonneClipping = [
    "Eta_anni",
    "Pressione_Diastolica_mmHg",
    "Insulina_Sierica_2ore",
    "Indice_Massa_Corporea",
]

# Range clinici/anagrafici plausibili: valori fuori range -> NaN.
RangeValidi = {
    "Eta_anni": (14, 55),
    "Numero_Gravidanze_Pregresse": (0, 20),
    "Numero_Tagli_Cesarei_Pregressi": (0, 12),
    "Pressione_Diastolica_mmHg": (40, 130),
    "Insulina_Sierica_2ore": (0, 400),
    "Indice_Massa_Corporea": (14, 60),
}
