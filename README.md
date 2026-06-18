# Previsione Polidramnios

Piccolo progetto di ML che, a partire da alcuni dati clinici di una paziente,
stima la probabilità di **Polidramnios**. C'è la parte di analisi/training nei
notebook, un backend Flask che espone il modello e un frontend semplice per provarlo.

## Cosa c'è dentro
- `dataset/` – il CSV con i 10.000 pazienti
- `notebooks/` – `train.ipynb` (pulizia dati, analisi, addestramento) e `previsione.ipynb` (come usare il modello salvato)
- `models/` – il modello addestrato (`.joblib`), generato dal training
- `backend/` – API Flask + le funzioni di supporto per training e previsione
- `frontend/` – pagina HTML/CSS/JS per inserire i dati e vedere il risultato
- `mobile/` – app .NET MAUI (Android) che fa la stessa cosa del frontend, ma da telefono

## Installazione
```bash
python -m venv .venv
.venv\Scripts\activate          # su Windows
pip install -r backend/requirements.txt
```

## Come si usa

**1. Addestrare il modello** (se non c'è già in `models/`):
```bash
cd backend
python train.py
```
Stampa un report della pulizia e delle metriche, poi salva il modello in `models/`.

**2. Avviare il backend:**
```bash
cd backend
python app.py
```
Resta in ascolto su `http://127.0.0.1:5000`.

**3. Aprire il frontend:** apri `frontend/index.html` nel browser, compila i campi
(età, pressione, BMI calcolato da altezza e peso, ecc.) e premi *Calcola previsione*.

## App mobile (MAUI)
Stessa logica del frontend, ma come app .NET MAUI. Richiede .NET 10 SDK + workload
`maui` (per Android servono anche Android SDK/JDK). **Tieni il backend Flask avviato**
prima di usare l'app.

**Come finestra desktop Windows** (modo più rapido, niente emulatore):
```bash
cd mobile
dotnet build -f net10.0-windows10.0.19041.0 -c Debug -p:WindowsPackageType=None
./bin/Debug/net10.0-windows10.0.19041.0/win-x64/PolidramniosMobile.exe
```

**Su Android** (emulatore o dispositivo):
```bash
cd mobile
dotnet build -t:Run -f net10.0-android
```
Su emulatore Android il backend si raggiunge a `http://10.0.2.2:5000`, su Windows a
`http://127.0.0.1:5000` (entrambi già gestiti nel codice). In alternativa apri `mobile/`
in Visual Studio / VS Code (estensione .NET MAUI) e premi *Run*.

## Come funziona, in breve
I dati grezzi sono "sporchi" (numeri scritti a parole, unità nel testo, valori fuori
range): vengono ripuliti, ma senza buttare righe – gli outlier sono limitati, non
eliminati, perché i casi positivi sono pochi. Imputazione e normalizzazione stanno
dentro una Pipeline scikit-learn, così il modello (una Regressione Logistica scelta
con cross-validation sul ROC-AUC) non "sbircia" i dati di test. Il backend carica il
modello salvato e risponde con previsione (0/1) e probabilità; il frontend fa i
controlli sui campi e chiama l'API.