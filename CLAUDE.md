# Istruzioni di progetto (per Claude)

Regole da rispettare in questo progetto e riutilizzabili in progetti simili (ML +
backend + frontend). Aggiornare questo file ogni volta che vengono date nuove
istruzioni particolari sulla gestione del codice.

## Stile del codice
- Commentare **il giusto**: solo dove serve a capire il *perché*, non il *cosa* ovvio.
- Solo **codice essenziale**, niente over-engineering o funzioni inutili.
- Nei **notebook** usare `snake_case`; nei moduli del **backend** usare i nomi delle
  funzioni della correzione fornita (`PascalCase`: `CaricaDati`, `PulisciDati`,
  `Train_e_Seleziona_Modello_Migliore`, `Valuta_e_SalvaModello`, ...).
- Quando vengono fornite "correzioni"/soluzioni, confrontarle col codice e mantenerne
  le **accortezze**, adattando lo stile a quello già presente.
- **Verificare sempre** il codice eseguendolo (script/replay) prima di dichiararlo
  funzionante. Niente affermazioni di "fatto" senza prova.

## Accortezze Machine Learning (dataset clinico sbilanciato)
- **Niente data leakage**: imputazione e scaling vanno **dentro la Pipeline**
  (`SimpleImputer`, `StandardScaler`), così il fit resta solo sul train. Non imputare
  sull'intero dataset prima dello split.
- **Outlier → clipping, non rimozione di righe**: la classe positiva è rara (~2-3%),
  rimuovere righe perderebbe casi positivi. Clip = IQR ∩ range clinico.
- **Range clinici/anagrafici**: valori fuori range → `NaN` (imputati poi dalla Pipeline).
- **Coerenza logica**: correggere inconsistenze impossibili (es. tagli cesarei >
  gravidanze pregresse → portati al massimo ammesso).
- **Dati sporchi**: parsing robusto (numeri a parole, unità nel testo, virgola
  decimale, Sì/No) → `NaN` se non interpretabile. Non usare il solo `pd.to_numeric`.
- **Modello**: Regressione Logistica con `class_weight='balanced'`, `max_iter=2000`.
- **Selezione**: `GridSearchCV` su `StratifiedKFold(5)`, `scoring='roc_auc'` (NON
  accuracy, dataset sbilanciato). Split `train_test_split(..., stratify=y)`.
- **Valutazione**: guardare soprattutto recall / F1 / ROC-AUC, non l'accuracy.
- **Salvataggio**: pacchetto `joblib` con `pipeline`, `features`, `target`,
  `threshold`, `metrics`. Le `features` servono al frontend per l'ordine input.

## Struttura del progetto
```
dataset/     dataset CSV
models/      modello .joblib (output del training)
notebooks/   train.ipynb (EDA + training), previsione.ipynb (uso del modello)
backend/     config.py + train_utils.py + predizione_utils.py + train.py + app.py
frontend/    index.html + style.css + app.js
mobile/      app .NET MAUI (PolidramniosMobile) — client Android dell'API
```
- I **percorsi** sono relativi alla root del progetto (`config.py` usa
  `Path(__file__).resolve().parent.parent`). Nei notebook i path sono relativi a
  `notebooks/` (es. `../dataset/...`, `../models/...`).
- `config.py` centralizza percorsi e costanti delle colonne (feature, continue,
  binarie, clipping, range). Non duplicare queste costanti altrove.

## Backend (Flask)
- Semplice ma ben organizzato: due file di supporto (`train_utils`, `predizione_utils`)
  col codice dei notebook riadattato; `train.py` orchestratore con **report** a video;
  `app.py` espone gli endpoint.
- Modello caricato **una volta** all'avvio, non a ogni richiesta.
- **Validazione input al confine** (`/previsione`): tutte le feature presenti e
  convertibili a `float`, altrimenti `400` con messaggio chiaro.
- **CORS** abilitato (`flask-cors`) per le chiamate dal frontend.

## Frontend
- Solo `html` + `css` + `javascript` essenziale, niente framework JS pesanti.
- Estetica pulita e coerente col contesto (Bootstrap + CSS custom).
- Gestione errori completa: campi obbligatori, range dei campi, input non numerico
  segnalato (niente POST se invalido), errori di rete/server mostrati all'utente.
- Booleani con checkbox/switch.
- Calcoli derivati lato JS prima del POST (es. BMI da altezza + peso).

## App mobile (.NET MAUI 10)
- Progetto in `mobile/` (`PolidramniosMobile`), target principale `net10.0-android`.
- Stesse regole del frontend: validazione (obbligatori, range, non numerico), switch per
  i booleani, BMI calcolato in app da altezza + peso prima della chiamata.
- Chiamata HTTP al backend via `HttpClient` (`Services/PrevisioneService.cs`). Base URL:
  `10.0.2.2:5000` su Android (emulatore → host), `127.0.0.1:5000` altrove.
- Android: serve `usesCleartextTraffic="true"` nel manifest per HTTP in chiaro.
- UI con `Border` (non `Frame`, deprecato dal .NET 9). Handler eventi con `object?`.
- Dipendenze di build (già installate qui): .NET 10 SDK, workload `maui`, Android SDK + JDK.

## Accessibilità (UI: frontend e mobile)
- **Label sempre visibile** sopra/accanto a ogni input: il placeholder non basta (sparisce
  quando si digita e ha contrasto basso). Il placeholder serve solo per esempio/range.
- **Contrasto adeguato** testo/sfondo: testo scuro (`#2a3b3d`) su sfondo chiaro. Mirare al
  rapporto WCAG AA (≥ 4.5:1 per testo normale). Niente testo grigio chiaro su bianco.
- **Niente colore come unico segnale**: l'esito usa testo esplicito ("Rischio di
  Polidramnios" / "Nessun rischio rilevato"), non solo rosso/verde.
- **Tema controllato**: forzare il tema chiaro (`UserAppTheme = AppTheme.Light` in MAUI)
  finché non è previsto un tema scuro testato, così il dark mode di sistema non rende il
  testo illeggibile.
- **Campi numerici**: `Keyboard="Numeric"` (MAUI) / `type="number"` o `inputmode` (web) per
  facilitare l'inserimento.
- **Messaggi d'errore testuali e specifici**, vicino all'azione, che dicono cosa correggere
  (campo + motivo), non solo un bordo rosso.
- **Target tappabili** adeguati (switch/bottoni) e label associate ai controlli (nel web usare
  `<label for>`).
