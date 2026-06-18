"""Funzioni di supporto per l'addestramento del modello Polidramnios.

Codice adattato dal notebook `train.ipynb` per l'uso da backend: stessa logica
(pulizia, preprocessore, training, valutazione) organizzata in funzioni riusabili.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
)

from config import (
    PercorsoDati, PercorsoModello, ColonnaTarget, ColonneFeatures,
    ColonneContinue, ColonneBinarie, ColonneClipping, RangeValidi,
)


# --- Parsing di valori "sporchi" ------------------------------------------------
PAROLE = {"zero": 0, "uno": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5,
          "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10}


def _to_num(v):
    """Estrae un numero da una stringa sporca (es. '32 anni', 'nove', '60,8'); NaN se impossibile."""
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower().replace(",", ".")
    if s in PAROLE:
        return float(PAROLE[s])
    m = re.search(r"-?\d+\.?\d*", s)
    return float(m.group()) if m else np.nan


def _to_bin(v):
    """Converte Si'/No/0/1 in 0.0/1.0; NaN se non interpretabile."""
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower()
    if s in ("1", "si", "sì", "s"):
        return 1.0
    if s in ("0", "no", "n"):
        return 0.0
    return np.nan


def CaricaDati(csv_path: Path = PercorsoDati) -> pd.DataFrame:
    """Carica il dataset CSV."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"File CSV non trovato: {csv_path}")
    return pd.read_csv(csv_path)


def PulisciDati(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Pulisce i dati e restituisce (df_pulito, report dei conteggi).

    Passi:
    - converte le colonne in numerico, gestendo testo sporco
    - valori binari non 0/1 -> NaN
    - elimina righe con target mancante
    - valori fuori range clinico -> NaN
    - corregge l'inconsistenza cesarei > gravidanze
    - clippa gli outlier (IQR ∩ range clinico), senza eliminare righe
    I NaN residui restano: li imputa la Pipeline (così niente data leakage).
    """
    df = df.copy()
    report: Dict[str, int] = {}

    colonne_attese = ColonneFeatures + [ColonnaTarget]
    mancanti = [c for c in colonne_attese if c not in df.columns]
    if mancanti:
        raise ValueError(f"Colonne mancanti nel CSV: {mancanti}")
    df = df[colonne_attese]

    # Conversione a numerico (testo non interpretabile -> NaN).
    for c in ColonneContinue:
        prima = df[c].isna().sum()
        df[c] = df[c].map(_to_num)
        report[f"valori_non_numerici_{c}"] = int(df[c].isna().sum() - prima)
    for c in ColonneBinarie:
        prima = df[c].isna().sum()
        df[c] = df[c].map(_to_bin)
        report[f"valori_non_binari_{c}"] = int(df[c].isna().sum() - prima)

    # Target deve essere 0/1; le righe senza target non servono per addestrare.
    df[ColonnaTarget] = pd.to_numeric(df[ColonnaTarget], errors="coerce")
    report["righe_rimosse_target_mancante"] = int(df[ColonnaTarget].isna().sum())
    df = df.dropna(subset=[ColonnaTarget])
    df[ColonnaTarget] = df[ColonnaTarget].astype(int)

    # Range clinici: valori fuori range -> NaN.
    for c, (lo, hi) in RangeValidi.items():
        mask = ((df[c] < lo) | (df[c] > hi)) & df[c].notna()
        report[f"valori_fuori_range_{c}"] = int(mask.sum())
        df.loc[mask, c] = np.nan

    # Coerenza logica: i cesarei pregressi non possono superare le gravidanze pregresse.
    inc = (
        df["Numero_Tagli_Cesarei_Pregressi"].notna()
        & df["Numero_Gravidanze_Pregresse"].notna()
        & (df["Numero_Tagli_Cesarei_Pregressi"] > df["Numero_Gravidanze_Pregresse"])
    )
    report["righe_corrette_cesarei_maggiori_gravidanze"] = int(inc.sum())
    df.loc[inc, "Numero_Tagli_Cesarei_Pregressi"] = df.loc[inc, "Numero_Gravidanze_Pregresse"]

    # Outlier: clipping (IQR intersecato con i range clinici), senza rimuovere righe.
    for c in ColonneClipping:
        s = df[c].dropna()
        if s.empty:
            report[f"outlier_clippati_{c}"] = 0
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        lo_clin, hi_clin = RangeValidi[c]
        low, high = max(low, lo_clin), min(high, hi_clin)
        mask = ((df[c] < low) | (df[c] > high)) & df[c].notna()
        report[f"outlier_clippati_{c}"] = int(mask.sum())
        df[c] = df[c].clip(lower=low, upper=high)

    return df, report


def AnalisiEsplorativa(df: pd.DataFrame) -> None:
    """Stampa media, mediana, deviazione standard e valori mancanti."""
    stats = df[ColonneFeatures + [ColonnaTarget]].agg(["mean", "median", "std"]).T
    print("\n=== Statistiche descrittive ===")
    print(stats.round(3))
    print("\n=== Valori mancanti (dopo pulizia) ===")
    print(df.isna().sum())


def AnalisiCorrelazione(df: pd.DataFrame) -> None:
    """Stampa le correlazioni delle feature con il target (ordinate per intensità)."""
    corr = df[ColonneFeatures + [ColonnaTarget]].corr(numeric_only=True)
    corr_target = corr[ColonnaTarget].drop(ColonnaTarget)
    corr_target = corr_target.reindex(corr_target.abs().sort_values(ascending=False).index)
    print("\n=== Correlazioni con il target Polidramnios ===")
    print(corr_target.round(3))


def Preprocessor() -> ColumnTransformer:
    """Preprocessore: continue imputate (mediana) + scalate; binarie imputate (moda).

    Imputazione e scaling vivono nella Pipeline -> il fit resta sul solo train.
    """
    pipe_continue = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    pipe_binarie = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])
    return ColumnTransformer(
        transformers=[
            ("continue", pipe_continue, ColonneContinue),
            ("binarie", pipe_binarie, ColonneBinarie),
        ],
        remainder="drop",
    )


def Train_e_Seleziona_Modello_Migliore(df: pd.DataFrame) -> Tuple[GridSearchCV, pd.DataFrame, pd.Series]:
    """Split stratificato + GridSearchCV (ROC-AUC) su Regressione Logistica.

    Ritorna (grid_search, X_test, y_test).
    """
    X = df[ColonneFeatures]
    y = df[ColonnaTarget]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y,
    )

    # Regressione Logistica: probabilistica, interpretabile, class_weight='balanced'
    # per la classe positiva rara (~2-3%). Ottimizzo il ROC-AUC, non l'accuracy.
    pipeline = Pipeline([
        ("preprocessor", Preprocessor()),
        ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])
    param_grid = {"classifier__C": [0.01, 0.1, 1.0, 10.0, 100.0]}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(pipeline, param_grid, scoring="roc_auc", cv=cv, n_jobs=-1, verbose=1)

    print("\n=== Avvio ricerca parametri migliori ===")
    grid.fit(X_train, y_train)
    print("\n=== Migliori parametri ===")
    print(grid.best_params_)
    print(f"Miglior ROC-AUC medio in cross-validation: {grid.best_score_:.4f}")
    return grid, X_test, y_test


def Valuta_e_SalvaModello(grid: GridSearchCV, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Valuta il modello migliore sul test set e salva il pacchetto joblib. Ritorna le metriche."""
    PercorsoModello.parent.mkdir(parents=True, exist_ok=True)
    modello = grid.best_estimator_
    y_pred = modello.predict(X_test)
    y_prob = modello.predict_proba(X_test)[:, 1]

    metriche = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "best_params": str(grid.best_params_),
        "best_cv_roc_auc": float(grid.best_score_),
    }

    print("\n=== Valutazione su test set ===")
    for k in ("accuracy", "precision", "recall", "f1", "roc_auc"):
        print(f"{k:10s}: {metriche[k]:.4f}")
    print("\nMatrice di confusione:\n", np.array(metriche["confusion_matrix"]))
    print("\nClassification report:\n", classification_report(y_test, y_pred, zero_division=0))

    pacchetto = {
        "pipeline": modello,
        "features": ColonneFeatures,
        "target": ColonnaTarget,
        "threshold": 0.50,
        "metrics": metriche,
    }
    joblib.dump(pacchetto, PercorsoModello)
    print("\nModello salvato in", PercorsoModello)
    return metriche