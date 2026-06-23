# Istruzioni di progetto (per Claude)

Regole generali per progetti di questo tipo (ML + backend + frontend, eventuale app
mobile), riusabili su qualsiasi traccia/dataset. Aggiornare questo file ogni volta che
vengono date nuove istruzioni particolari sulla gestione del codice.

> Per il playbook completo di costruzione da zero (fasi, checkpoint, template per tracce
> diverse) vedi [GUIDA_SVILUPPO.md](GUIDA_SVILUPPO.md).

## Contesto: progetto d'esame universitario
- È un esame: **la traccia fornita ha sempre la priorità** su queste regole generali.
  Se la traccia differisce da quanto scritto qui (dataset, tipo di problema, tecnologie,
  nomi richiesti, formato di output), **segnalarlo e chiedere all'utente** prima di
  procedere — non assumere in autonomia.
- **Analizzare sempre il dataset a fondo prima di decidere qualcosa** (modello, pulizia,
  costanti): nome, colonne, target, tipo di problema (classificazione/regressione/...),
  bilanciamento, sporcizia cambiano da traccia a traccia. Non riusare a memoria nomi o
  valori di un progetto precedente.
- **Ogni affermazione sul dataset va dimostrata con un calcolo reale** (output di
  `value_counts()`, `isna().sum()`, percentuali calcolate nel notebook), mai assunta o
  copiata da un altro progetto — anche se sembra un caso simile.
- **Scegliere modello e metrica in base al tipo di problema** rilevato nell'analisi, non
  assumere a priori un modello o una metrica: vanno scelti con i numeri (confronti in CV).
- Tempo limitato: prima una **fetta verticale funzionante** end-to-end (dato → modello →
  previsione), poi rifinire. Riproducibilità: `random_state` fisso, notebook che gira
  "Run All" dall'alto senza errori. Rispettare **esattamente** il formato richiesto dalla
  traccia (nomi file/modello, endpoint, struttura della risposta).

## Stile del codice
- **Codice minimo funzionante**: solo quanto serve, niente over-engineering, niente
  funzioni inutili.
- Commentare **il giusto**: solo dove serve a capire il *perché*, non il *cosa* ovvio.
  **Commenti in italiano**, in **linguaggio semplice da studente**, discorsivo — niente
  formule o termini troppo tecnici, spiegare il perché a parole proprie come lo si
  racconterebbe a voce.
- **Mai citare nei commenti queste istruzioni o una guida/checklist** (no
  `# come richiesto dalla traccia`, `# step della guida`): applicare le regole, non
  parlarne. Il commento deve sembrare ragionamento proprio.
- **Seguire sempre le best practice, niente workaround**: se qualcosa non funziona,
  trovare la causa e risolverla, non aggirarla.
- **Gestione errori curata sia nel backend sia nel frontend**: validazione input,
  messaggi chiari, nessun crash su input/condizioni inattese.
- Nei **notebook** usare `snake_case`; nei moduli del **backend** usare i nomi delle
  funzioni della correzione fornita (convenzione `PascalCase`: es. `CaricaDati`,
  `PulisciDati`, `Train_e_Seleziona_Modello_Migliore`, `Valuta_e_SalvaModello`, ...).
  Se la traccia/correzione richiede altri nomi, usare quelli.
- Quando vengono fornite "correzioni"/soluzioni, confrontarle col codice e mantenerne
  le **accortezze**, adattando lo stile a quello già presente.
- **Verificare sempre** il codice eseguendolo (script/replay) prima di dichiararlo
  funzionante. Niente affermazioni di "fatto" senza prova.

## Machine Learning: metodologia di training
Idea di fondo: **non dare niente per scontato, scegliere con i numeri.** Provare le
alternative in **cross-validation sul train** e confermare alla fine sul **test tenuto da
parte** (mai usato prima). Dimostrare le scelte con tabelle di confronto e spiegarne il
perché in modo semplice. Se la traccia impone modello/metrica, usare quelli.

- **Metriche scelte PRIMA di allenare** (guidano tuning e soglia):
  - classificazione **sbilanciata** → **NON usare l'accuracy**; usare **PR-AUC**
    (`average_precision`), recall, F1/F2; `roc_auc` come secondaria. (Baseline PR-AUC =
    percentuale di positivi, non 0.5.)
  - classificazione bilanciata → `f1`/`accuracy`; regressione → `r2`, `RMSE`, `MAE`.
- **Niente data leakage**: imputazione e scaling **dentro la Pipeline** (`SimpleImputer`,
  `StandardScaler`), fit solo sul train. Mai trasformare l'intero dataset prima dello split.
- **Preprocessing — confrontare le alternative in CV**: imputazione (mediana/media/KNN/
  iterative), scaling (standard/robust/minmax/nessuno), outlier **con e senza clipping**
  (a volte gli estremi sono il segnale). **Mai rimuovere righe** se i positivi sono pochi:
  outlier → **clipping** (IQR ∩ range plausibile). Feature engineering solo se aiuta davvero.
- **Valori fuori range** plausibile → `NaN` (imputati poi dalla Pipeline).
- **Coerenza logica**: correggere inconsistenze impossibili tra colonne (es. un
  sotto-conteggio che supera il totale → portato al massimo ammesso).
- **Dati sporchi**: parsing robusto (numeri a parole, unità nel testo, virgola decimale,
  Sì/No) → `NaN` se non interpretabile. Non usare il solo `pd.to_numeric`. Target mancante
  → riga eliminata.
- **Confronto modelli** (non fermarsi al primo): valutare in CV più famiglie — lineari,
  alberi/ensemble (RandomForest, Gradient/HistGradient Boosting), SVM, KNN, MLP, Naive
  Bayes. A parità di risultato, preferire il più **semplice e spiegabile**. Sbilanciamento
  → `class_weight='balanced'` dove supportato.
- **Iperparametri**: `GridSearchCV` con griglia **ampia**, `StratifiedKFold(5)` (classif.)
  o `KFold` (regress.), `scoring` adatto allo sbilanciamento. Split
  `train_test_split(..., test_size=0.20, random_state=42, stratify=y)` (stratify se classif.).
- **Soglia di decisione** (classificazione binaria): non lasciarla a 0.50; calcolarla in CV
  sul train con una metrica legata al **costo degli errori** (es. F2). Salvarla col modello.
- **Valutazione finale** sul test tenuto da parte: metriche scelte, matrice di confusione,
  `classification_report` (classif.) o `R²/RMSE/MAE` (regress.).
- **Salvataggio**: pacchetto `joblib` con `pipeline`, `features`, `target`, `metrics`
  (+ `threshold` se classificazione binaria). Le `features` servono al frontend/mobile per
  l'ordine degli input.

## Struttura del progetto
```
dataset/     dataset CSV
models/      modello .joblib (output del training)
notebooks/   train.ipynb (EDA + pulizia + training), predict.ipynb (uso del modello)
backend/     config.py + train_utils.py + predizione_utils.py + train.py + app.py
frontend/    index.html + style.css + app.js
mobile/      app .NET MAUI — client dell'API (solo se la traccia la richiede)
```
- I **percorsi** sono relativi alla root del progetto (`config.py` usa
  `Path(__file__).resolve().parent.parent`). Nei notebook i path sono relativi a
  `notebooks/` (es. `../dataset/...`, `../models/...`).
- `config.py` centralizza percorsi e costanti delle colonne (feature, continue, binarie,
  clipping, range), ricavate dall'analisi del dataset. Non duplicare queste costanti altrove.
- **`requirements.txt` unico in root**, senza numeri di versione delle librerie (una per
  riga). Evitare di duplicarlo per sottoprogetto a meno che non sia strettamente necessario.

## Backend (Flask)
- Semplice ma ben organizzato: due file di supporto (`train_utils`, `predizione_utils`)
  col codice dei notebook riadattato; `train.py` orchestratore con **report** a video;
  `app.py` espone gli endpoint.
- Modello caricato **una volta** all'avvio, non a ogni richiesta.
- **Validazione input al confine** (endpoint di previsione): tutte le feature presenti e
  del tipo atteso (es. convertibili a `float`), altrimenti `400` con messaggio chiaro.
  Se il modello manca, l'endpoint risponde `503`.
- **CORS** abilitato (`flask-cors`) per le chiamate dal frontend.
- **Endpoint preset** (`GET /preset`): legge un file JSON nel backend (es.
  `backend/preset.json`) con **3 set di dati di esempio** e li restituisce. Frontend e
  mobile lo chiamano per popolare i campi con un click. Il file è la singola fonte dei
  preset (niente dati duplicati nel client).

## Frontend
- Solo `html` + `css` + `javascript` essenziale, niente framework JS pesanti.
- Estetica pulita e coerente col contesto (Bootstrap + CSS custom).
- Gestione errori completa: campi obbligatori, range dei campi, input non numerico
  segnalato (niente POST se invalido), errori di rete/server mostrati all'utente.
- Booleani con checkbox/switch.
- Calcoli derivati lato JS prima del POST quando previsti dal dominio (es. un valore
  calcolato da altri due campi), inviando solo le feature richieste dal modello.
- **Pulsante preset**: carica i 3 preset da `GET /preset` e, con un click, inserisce i
  dati nei campi input (mantenendo coerente l'estetica dell'app). Utile per provare in
  fretta senza digitare.
- **Storico delle valutazioni**: a ogni previsione riuscita, salvare in `localStorage`
  (persistente, sopravvive al refresh) **sia gli input sia l'esito**. Mostrare una lista
  con data/ora, input usati, esito e probabilità, più un pulsante per **svuotare** lo
  storico. **Cliccando una voce**, ricaricare nei campi gli input di quell'analisi.

## App mobile (.NET MAUI 10) — solo se la traccia la richiede
- Progetto in `mobile/`, target principale `net10.0-android`.
- Stesse regole del frontend: validazione (obbligatori, range, non numerico), switch per
  i booleani, eventuali calcoli derivati fatti in app prima della chiamata.
- **Pulsante preset**: carica i 3 preset da `GET /preset` e li inserisce nei campi con un
  tap (estetica coerente con l'app).
- **Storico delle valutazioni**: a ogni previsione riuscita, salvare in modo persistente
  (`Preferences` o file locale) **sia gli input sia l'esito**: lista con data/ora, input,
  esito e probabilità, più un pulsante per **svuotare** lo storico. **Toccando una voce**,
  ricaricare nei campi gli input di quell'analisi.
- Chiamata HTTP al backend via `HttpClient` (`Services/PrevisioneService.cs`). Base URL:
  `10.0.2.2:5000` su Android (emulatore → host), `127.0.0.1:5000` altrove.
- Android: serve `usesCleartextTraffic="true"` nel manifest per HTTP in chiaro.
- UI con `Border` (non `Frame`, deprecato dal .NET 9). Handler eventi con `object?`.
- Dipendenze di build: .NET 10 SDK, workload `maui`, Android SDK + JDK.

## Accessibilità (UI: frontend e mobile)
- **Label sempre visibile** sopra/accanto a ogni input: il placeholder non basta (sparisce
  quando si digita e ha contrasto basso). Il placeholder serve solo per esempio/range.
- **Contrasto adeguato** testo/sfondo: testo scuro (es. `#2a3b3d`) su sfondo chiaro. Mirare
  al rapporto WCAG AA (≥ 4.5:1 per testo normale). Niente testo grigio chiaro su bianco.
- **Niente colore come unico segnale**: l'esito usa **testo esplicito** (es. "Esito
  positivo" / "Esito negativo" o l'equivalente nel dominio), non solo rosso/verde.
- **Tema controllato**: forzare il tema chiaro (`UserAppTheme = AppTheme.Light` in MAUI)
  finché non è previsto un tema scuro testato, così il dark mode di sistema non rende il
  testo illeggibile.
- **Campi numerici**: `Keyboard="Numeric"` (MAUI) / `type="number"` o `inputmode` (web) per
  facilitare l'inserimento.
- **Messaggi d'errore testuali e specifici**, vicino all'azione, che dicono cosa correggere
  (campo + motivo), non solo un bordo rosso.
- **Target tappabili** adeguati (switch/bottoni) e label associate ai controlli (nel web usare
  `<label for>`).
