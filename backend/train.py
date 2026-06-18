"""Script di addestramento: esegue l'intera procedura con report a video.

Uso:  python train.py
"""
from config import PercorsoDati
from train_utils import (
    CaricaDati, PulisciDati, AnalisiEsplorativa, AnalisiCorrelazione,
    Train_e_Seleziona_Modello_Migliore, Valuta_e_SalvaModello,
)


def main() -> None:
    print(f"Caricamento dati da: {PercorsoDati}")
    DataFrameNonElaborato = CaricaDati(PercorsoDati)
    print(f"Dataset originale: {DataFrameNonElaborato.shape[0]} righe, "
          f"{DataFrameNonElaborato.shape[1]} colonne")

    DataFramePulito, ReportPuliziaEffettuata = PulisciDati(DataFrameNonElaborato)
    print(f"Dataset dopo pulizia: {DataFramePulito.shape[0]} righe, "
          f"{DataFramePulito.shape[1]} colonne")

    print("\n=== Report pulizia ===")
    for key, value in ReportPuliziaEffettuata.items():
        print(f"{key}: {value}")

    AnalisiEsplorativa(DataFramePulito)
    AnalisiCorrelazione(DataFramePulito)

    grid_search, X_test, y_test = Train_e_Seleziona_Modello_Migliore(DataFramePulito)
    Valuta_e_SalvaModello(grid_search, X_test, y_test)


if __name__ == "__main__":
    main()