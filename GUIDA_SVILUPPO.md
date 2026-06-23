# Guida di sviluppo — Playbook per costruire il progetto da zero

> **A cosa serve questo file.** È un *playbook* da incollare a Claude (o da seguire a
> mano) per **costruire l'intero progetto da zero**, nell'ordine giusto, con tutte le
> accortezze da rispettare. Pensato come allenamento d'esame (`sim_esam`).
>
> **⚠️ La traccia d'esame ha SEMPRE la priorità.** Questa guida descrive il *metodo* e le
> *buone pratiche*; i dettagli concreti (dataset, target, tipo di problema, nomi funzioni,
> tecnologie richieste) li detta la **traccia**. Tutto ciò che qui è scritto in stile
> `<segnaposto>` o marcato come *esempio* va riempito leggendo la traccia + il dataset.
>
> Progetto di esempio già realizzato in questo repo: **Previsione Polidramnios**
> (classificazione binaria sbilanciata). Usalo come riferimento di stile, **non** come
> specifica fissa.

---

## 0. Istruzioni per Claude (leggere PRIMA di toccare codice)

1. **La traccia comanda.** All'inizio ti verrà fornita la **traccia d'esame**.
   - **Confronta** la traccia con questa guida. Se qualcosa **differisce** (tecnologia,
     tipo di problema, struttura richiesta, vincoli, output attesi, nomi, ecc.),
     **fermati e segnalalo esplicitamente all'utente, chiedendo come procedere.**
   - In ogni conflitto **vince la traccia**: questa guida è solo metodo e default ragionevoli.
2. **Prima di cominciare, fai domande.** Non scrivere codice finché non hai chiarito i
   dubbi. Domande tipiche: dove e com'è il dataset? Qual è il target? È classificazione o
   regressione? Quali tecnologie/librerie impone la traccia? Serve mobile? Solo quando
   l'utente dà l'OK, procedi.
3. **Analizza il dataset a fondo PRIMA di tutto** (vedi §2). Niente assunzioni sui nomi o
   sul contenuto delle colonne: vanno letti dal dataset reale.
4. **Lavora a fasi, con checkpoint.** Lo sviluppo è diviso in fasi (sotto). **Alla fine di
   ogni fase FERMATI** e aspetta che l'utente revisioni, corregga e confermi prima di
   passare alla successiva. Stop marcati con **⛔ STOP**.
5. **Verifica sempre eseguendo.** Niente "fatto" senza prova: esegui notebook/script, avvia
   il server, mostra l'output reale. Se qualcosa fallisce, dillo.
6. **Stile del codice:**
   - **Codice minimo funzionante**: scrivi solo quello che serve a far funzionare la
     richiesta, niente più. Niente over-engineering, niente funzioni inutili.
   - **Commenti in italiano**, ben fatti: commenta **il giusto** spiegando il *perché*
     (le scelte, le accortezze), non il *cosa* ovvio. Niente commenti in inglese.
   - **Linguaggio dei commenti da studente**, semplice e discorsivo: spiega il perché con
     parole tue, come lo racconteresti a voce, **non** con formule o termini troppo tecnici.
     Es. non `# clip = IQR ∩ range clinico per evitare leakage`, ma
     `# tolgo i valori troppo estremi senza buttare la riga, perché i casi positivi sono pochi
     e non me li posso permettere di perdere`.
   - **Mai citare nei commenti (né nei notebook né nel codice) queste istruzioni o il fatto
     che stai seguendo una guida/checklist.** Applica le regole, non parlarne: niente
     `# come richiesto dalle linee guida`, `# secondo la traccia`, `# step 3 della guida`.
     È un esame: il commento deve sembrare ragionamento tuo, non l'esecuzione di un piano.
   - **Segui sempre le best practice e NON usare workaround**: niente scorciatoie o
     "trucchi" per far passare il codice. Se qualcosa non funziona, trova la causa e
     risolvi bene, non aggirare il problema.
   - Nei **notebook** usa `snake_case`; nei **moduli backend** usa i nomi delle funzioni
     della **correzione/traccia fornita** (convenzione di questo progetto: `PascalCase`,
     es. `CaricaDati`, `PulisciDati`, ...). Se la traccia/correzione usa altri nomi,
     **usa quelli**.
   - **Gestione errori curata** sia nel **backend** sia nel **frontend** (vedi Fase 2):
     validazione degli input, messaggi chiari, nessun crash su input/condizioni inattese.
   - File sotto le ~500 righe. Niente file di lavoro in root: usa `backend/`, `frontend/`,
     ecc. (eccezione: `README.md` e questo file).
7. **Ordine delle fasi (NON saltare):**
   `Fase 1 notebook` → ⛔ → `Fase 2 backend + frontend` → ⛔ → `Fase 3 mobile (se richiesta)`
   → ⛔ → `Fase 4 README`.

---

## 0bis. Contesto d'esame universitario

Questo è un progetto **d'esame**: oltre a "funzionare", conta *come* arrivi al risultato.

- **La traccia è anche la griglia di valutazione.** Ogni richiesta esplicita = punti.
  Rispondi a **tutte** le richieste, nell'ordine e nel formato chiesti. Non aggiungere
  funzionalità non richieste (non danno punti e tolgono tempo).
- **Tempo limitato → prima una fetta verticale funzionante.** Fai girare end-to-end il
  percorso minimo (dato → modello → previsione) *prima* di rifinire EDA, grafici, UI.
  Un progetto incompleto ma eseguibile vale più di uno perfetto a metà.
- **Rispetta ESATTAMENTE il formato richiesto**: nomi di file/modello, nomi colonne,
  nomi/percorsi degli endpoint, struttura della risposta JSON. Se la traccia dice
  `POST /predict` o un certo nome di `.joblib`, usali identici.
- **Giustifica le scelte.** Nel notebook usa **celle markdown** (e docstring nei moduli)
  per spiegare *perché* quel modello, quella metrica, quella pulizia. Gli esaminatori
  valutano il **ragionamento**, non solo l'output.
- **Riproducibilità**: `random_state` fisso ovunque; il notebook deve girare **"Run All"
  dall'alto in basso senza errori**; niente celle morte o che dipendono da un ordine di
  esecuzione manuale. Stesso input → stesso risultato.
- **Usa solo strumenti permessi** dalla traccia/regolamento (librerie, eventuale accesso a
  internet/AI). Nel dubbio, chiedi all'utente.
- **Salva spesso** il lavoro (commit incrementali) per non perdere progressi.

### ⚠️ Errori che fanno perdere punti (da evitare)
- **Data leakage**: imputare/scalare prima dello split o fuori dalla Pipeline.
- **Accuracy come metrica su dataset sbilanciato** (usa PR-AUC/recall/F1; ROC-AUC come secondaria).
- **Rimuovere righe per gli outlier** invece di clippare (perdi casi positivi rari).
- **Fermarsi al primo modello / al primo preprocessing** senza confrontare le alternative in CV.
- **Lasciare la soglia a 0.50** senza averla scelta con un'analisi (su classificazione binaria).
- **Affermare cose sul dataset senza dimostrarle** con un calcolo mostrato (es. "% di positivi").
- **Valori hardcoded** (nomi colonne, soglie, path) sparsi nel codice invece che in `config.py`.
- **Path assoluti** della tua macchina: usa percorsi relativi (`Path(__file__)...`, `../`).
- **Nessuna validazione input** al confine dell'API o nel frontend.
- **Notebook che non gira pulito** da capo o pieno di prove/celle commentate.

---

## 1. Struttura del progetto (default — adattare alla traccia)

```
dataset/     <nome_dataset>.csv                    (dato di partenza, fornito)
models/      <nome_modello>.joblib                 (output del training)
notebooks/   train.ipynb        (EDA + pulizia + training)
             predict.ipynb      (uso del modello salvato)
backend/     config.py          (percorsi + costanti colonne)
             train_utils.py     (funzioni di training, dal notebook)
             predizione_utils.py(funzioni di previsione, dal notebook)
             train.py           (orchestratore con report a video)
             app.py             (API Flask)
requirements.txt                (UNICO file in root, vedi Fase 0)
frontend/    index.html + style.css + app.js
mobile/      app .NET MAUI — client dell'API (solo se la traccia lo richiede)
README.md    (in root, ultimo passo)
```

- **Percorsi backend**: relativi alla root via `Path(__file__).resolve().parent.parent`.
- **Percorsi notebook**: relativi a `notebooks/` (es. `../dataset/...`, `../models/...`).
- `config.py` **centralizza** percorsi e costanti delle colonne. **Non duplicarle** altrove:
  backend e frontend ne replicano i valori in modo coerente.
- I nomi `<...>` e la presenza del modulo mobile dipendono dalla traccia.

---

## 2. Analisi del dataset (PRIMA FASE OBBLIGATORIA, prima di scrivere training)

Nome, contenuto, colonne, target, tipo di problema **cambiano a seconda della traccia**.
Quindi: **carica il dataset e analizzalo a fondo** prima di decidere qualsiasi cosa.

Cosa determinare dall'analisi (e poi riportare all'utente):

1. **Colonne**: nomi esatti, tipo (numerico/categorico/testo), unità, esempi di valori.
2. **Target**: qual è la colonna da prevedere; quali valori assume.
3. **Tipo di problema** (decide modello e metriche — vedi §3):
   - target categorico a 2 classi → **classificazione binaria**;
   - target categorico a >2 classi → **classificazione multiclasse**;
   - target numerico continuo → **regressione**;
   - nessun target → eventuale clustering (raro in queste tracce).
4. **Bilanciamento** (se classificazione): distribuzione delle classi. Classe positiva
   rara? (cambia metrica e `class_weight`).
5. **Qualità/sporcizia dei dati**: valori mancanti, numeri scritti a parole, unità nel
   testo, virgole decimali, Sì/No, outlier, valori fuori range plausibile, incoerenze
   logiche tra colonne.
6. **Range plausibili** per ogni colonna (clinici/anagrafici/fisici): servono a portare i
   fuori-range a `NaN` e a delimitare il clipping.

> Compila un piccolo "dizionario delle colonne" (nome → tipo, range, note) e proponilo
> all'utente. Le costanti che ne derivano vanno in `config.py`
> (`ColonnaTarget`, `ColonneFeatures`, `ColonneContinue`, `ColonneBinarie`,
> `ColonneClipping`, `RangeValidi`, o gli equivalenti che la traccia richiede).

**Tutto deve essere dimostrato, niente numeri a caso.** Ogni affermazione sul dataset
(es. "la classe positiva è rara", "il 5% dei valori manca", "c'è uno sbilanciamento") deve
venire da un **calcolo reale eseguito nel notebook** (`value_counts()`, `isna().sum()`,
percentuali calcolate), con l'output mostrato sotto la cella. Non scrivere/assumere una
percentuale o un'osservazione senza prima averla calcolata e vista nell'output — anche se
sembra "ovvia" o simile a un altro progetto.

---

## 3. Training: scelta del modello e accortezze (in base al problema)

**Idea di fondo: non dare niente per scontato, scegliere con i numeri.** Si provano le
alternative in **cross-validation sul train** e si conferma alla fine sul **test tenuto da
parte** (mai usato prima). In alcuni punti conviene fermarsi e fare analisi in più, non
andare col pilota automatico. Le scelte vanno **dimostrate** (tabelle di confronto) e
**spiegate** (perché, in modo semplice). Se la traccia impone modello/metrica, usa quelli.

### 3a. Metriche giuste — sceglierle PRIMA di allenare
La metrica dipende dal problema e va decisa **prima** del training (guida tuning e soglia).
- **Classificazione sbilanciata**: **NON usare l'accuracy** (inganna). Usare **PR-AUC**
  (`average_precision`), **recall** e **F1/F2**; tenere `roc_auc` come secondo riferimento.
  Ricorda: per la PR-AUC il "tirare a indovinare" non è 0.5 ma la **percentuale di positivi**.
- **Classificazione bilanciata**: `f1`/`accuracy` secondo richiesta.
- **Regressione**: `r2`, `RMSE` (`neg_root_mean_squared_error`), `MAE`.

### 3b. Preprocessing — qui fare analisi in più (confrontare le alternative)
Tutto **dentro la Pipeline** (no data leakage): limiti/medie si calcolano solo sul train.
- **Niente data leakage**: imputazione (`SimpleImputer`) e scaling **dentro la Pipeline**,
  fit solo sul train. **Non** trasformare l'intero dataset prima dello split.
- **Imputazione**: confrontare mediana / media / KNN / iterative e tenere la migliore in CV.
- **Scaling**: confrontare standard / robust / minmax / nessuno.
- **Outlier → clipping, non rimozione di righe**: **mai rimuovere righe** se i positivi sono
  pochi (perdi casi). Confrontare **con e senza clipping**: a volte i valori estremi sono
  proprio il segnale e tagliarli peggiora. Clip = **IQR ∩ range plausibile**.
- **Valori fuori range** plausibile → `NaN` (poi imputati dalla Pipeline).
- **Coerenza logica**: correggere incoerenze impossibili tra colonne (es. un sotto-conteggio
  che supera il totale → portato al massimo ammesso).
- **Dati sporchi**: parsing robusto — numeri a parole, unità nel testo, virgola decimale,
  Sì/No → altrimenti `NaN`. **Non** affidarsi al solo `pd.to_numeric`.
- **Target mancante**: righe senza target si **eliminano**.
- **Feature engineering** (interazioni, selezione): tenerlo **solo se aiuta davvero** (provato in CV).

### 3c. Modello — qui fare analisi in più (confrontare più famiglie)
- **Non fermarsi al primo modello.** Confrontare in cross-validation più famiglie: lineari
  (`LogisticRegression`/`LinearRegression`), alberi/ensemble (`RandomForest`,
  `GradientBoosting`/`HistGradientBoosting`), `SVM`, `KNN`, rete neurale (`MLP`),
  `NaiveBayes`.
- A **parità di risultato**, preferire il modello **più semplice e spiegabile**.
- **Sbilanciamento**: `class_weight="balanced"` (modelli che lo supportano); `max_iter` alto
  se serve convergenza (es. `LogisticRegression(max_iter=2000)`).

### 3d. Iperparametri
- **Split**: `train_test_split(..., test_size=0.20, random_state=42)`; con classificazione
  `stratify=y`.
- `GridSearchCV` con **griglia ampia**, `StratifiedKFold(5)` (o `KFold` per regressione),
  `scoring` adatto allo sbilanciamento (es. `average_precision`).

### 3e. Soglia di decisione — qui fare analisi in più (non lasciare 0.50)
- Per la classificazione binaria, **non lasciare la soglia a 0.50 di default.**
- Calcolarla in **cross-validation sul train** con una metrica legata al **costo degli
  errori** (es. **F2** se mancare un positivo è peggio di un falso allarme).
- **Salvarla insieme al modello** (campo `threshold` del pacchetto).

### 3f. Verifica finale, salvataggio, documentazione
- **Valutare sul test tenuto da parte** (mai usato prima): metriche scelte in §3a, matrice
  di confusione, `classification_report` (classificazione) o `R²/RMSE/MAE` (regressione).
- **Dimostrare tutto con i numeri** (tabelle di confronto tra le alternative provate) e
  scrivere il **perché** delle scelte fatte (celle markdown / docstring).
- **Salvataggio (joblib)**: pacchetto dict con almeno
  `{"pipeline", "features", "target", "metrics"}` (+ `"threshold"` per la classificazione
  binaria). Le `features` servono a frontend/mobile per l'ordine degli input.

### Regole d'oro
- **Niente data leakage** (tutto nella Pipeline, fit solo sul train).
- **Riproducibilità**: `random_state` fisso ovunque.
- **Spiegare sempre il perché**, in modo semplice.

---

## FASE 0 — Scaffold (preparazione)

1. Crea le cartelle: `dataset/ models/ notebooks/ backend/ frontend/` (+ `mobile/` se richiesta).
2. Metti il CSV fornito in `dataset/`.
3. **`requirements.txt` UNICO in root, senza versioni** (una libreria per riga). Esempio di
   base (adatta a quel che la traccia/codice usa davvero):
   ```
   pandas
   numpy
   scikit-learn
   joblib
   matplotlib
   seaborn
   flask
   flask-cors
   ```
   > Se per qualche motivo serve separare, va bene anche un `requirements.txt` per
   > sottoprogetto — ma il default richiesto è **un solo file in root**. Niente numeri di
   > versione.
4. Crea/attiva il venv e installa:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Scrivi `backend/config.py` con percorsi e **le costanti delle colonne ricavate dall'analisi
   del dataset** (§2). Non inventare i nomi: usa quelli reali.

---

## FASE 1 — Notebook (`train.ipynb` + `predict.ipynb`)

**Obiettivo**: EDA + pulizia + training nel primo notebook; uso del modello nel secondo.
Stile `snake_case`, path relativi a `notebooks/`. Applica §2 (analisi) e §3 (scelta + accortezze).

### `train.ipynb`
1. **Caricamento** CSV (`../dataset/...`), shape iniziale.
2. **Analisi esplorativa del dataset** (§2): colonne, tipi, distribuzione del target, valori
   mancanti, sporcizia, range. Da qui decidi tipo di problema e approccio.
3. **Scelta metriche PRIMA di allenare** (§3a): decidi e motiva le metriche in base al
   problema/bilanciamento (es. sbilanciato → PR-AUC/recall/F1, non accuracy).
4. **Pulizia** (accortezze §3b): parsing dello sporco, fuori-range → `NaN`, correzione
   incoerenze, clipping IQR ∩ range, rimozione righe con target mancante. Tieni un **report**
   dei conteggi (quante righe corrette/clippate/ecc.).
5. **Preprocessore** (`ColumnTransformer`): colonne continue → imputer + scaler; colonne
   binarie/categoriche → imputer (e encoding se serve); `remainder="drop"`. Dove sensato,
   **confronta in CV le alternative** di imputazione/scaling/clipping (§3b).
6. **Confronto modelli** (§3c): valuta in cross-validation più famiglie e tieni il migliore
   (a parità, il più semplice/spiegabile). Mostra la **tabella di confronto**.
7. **Tuning iperparametri** (§3d): `GridSearchCV` con griglia ampia, `StratifiedKFold(5)`,
   `scoring` adatto (es. `average_precision`).
8. **Scelta soglia** (§3e, solo classificazione binaria): calcolala in CV sul train con una
   metrica legata al costo degli errori (es. F2), non lasciarla a 0.50.
9. **Valutazione finale** sul test tenuto da parte (§3f): metriche scelte + matrice di
   confusione / report. Dimostra con numeri, spiega il perché.
10. **Salvataggio** pacchetto joblib in `../models/<nome_modello>.joblib`
    (`pipeline`, `features`, `target`, `metrics`, + `threshold` se binaria).

### `predict.ipynb`
- Carica il pacchetto joblib, costruisce **una riga** `DataFrame` con le feature
  nell'**ordine** di `pacchetto["features"]`, esegue la previsione (con `threshold` se
  classificazione binaria) → output `{"previsione"/valore, "probabilita"(se applicabile)}`.
  Mostra un esempio.

### Verifica fase 1
- Esegui i due notebook end-to-end senza errori; il `.joblib` viene creato; le metriche
  hanno senso per il tipo di problema.

> ⛔ **STOP** — Consegna i notebook all'utente. Aspetta revisione, correzione e conferma.
> **Non** procedere al backend prima dell'OK. Integra le accortezze di eventuali correzioni
> adattando lo stile a quello già presente.

---

## FASE 2 — Backend (Flask) + Frontend

Parti **dopo** l'OK sui notebook. Riadatta il codice dei notebook in moduli backend,
mantenendo i **nomi delle funzioni** richiesti dalla traccia/correzione (convenzione del
progetto: `PascalCase`).

### Backend
- `train_utils.py` — funzioni di training dal `train.ipynb` (es., adattando i nomi alla
  traccia: `CaricaDati`, `PulisciDati` → `(df, report)`, analisi/EDA, `Preprocessor`,
  `Train_e_Seleziona_Modello_Migliore` → `(grid, X_test, y_test)`, `Valuta_e_SalvaModello`
  → metriche). Più gli helper di parsing dello sporco.
- `predizione_utils.py` — `CaricaModello(percorso)` e una funzione di previsione su singolo
  input: `dati: dict + pacchetto -> risultato`.
- `train.py` — orchestratore: carica → pulisce → stampa **report pulizia** → EDA → training
  → valuta e salva. Tutto con report a video.
- `app.py` — API Flask:
  - **CORS abilitato** (`flask-cors`) per il frontend.
  - Modello **caricato una volta all'avvio** (non a ogni richiesta); se manca, `/health` lo
    segnala e l'endpoint di previsione risponde `503`.
  - `GET /health` → stato + `modello_caricato: bool`.
  - `POST /previsione` → body JSON con **tutte le feature**. **Validazione al confine**:
    tutte presenti e convertibili al tipo atteso, altrimenti `400` con messaggio chiaro +
    elenco feature richieste. Risponde con la previsione (+ probabilità se classificazione).
  - `GET /preset` → legge un file JSON nel backend (es. `backend/preset.json`) con **3 set
    di dati di esempio** (una lista di 3 oggetti, chiavi = nomi feature) e lo restituisce.
    È l'unica fonte dei preset: il client non li ridefinisce.
  - Avvio: `app.run(host="127.0.0.1", port=5000, debug=True)`.

### Frontend (`index.html` + `style.css` + `app.js`)
- Solo HTML + CSS + JS essenziale (Bootstrap + CSS custom ok), niente framework pesanti.
- **Calcoli derivati lato JS** prima del POST quando previsti dal dominio (es. BMI da altezza
  + peso: `peso / (altezza/100)²`; i campi ausiliari servono solo al calcolo, non si inviano).
- **Validazione completa** prima del POST (niente invio se invalido): obbligatorietà, valore
  numerico, range per campo, eventuali coerenze logiche tra campi.
- **Booleani** con checkbox/switch → 0/1.
- **Gestione errori di rete/server** mostrata all'utente (es. backend spento → messaggio chiaro).
- **Esito testuale** esplicito (non solo colore) + probabilità se disponibile.
- **Pulsante preset**: all'avvio carica i 3 preset da `GET /preset`; con un click inserisce
  i dati di un preset nei campi input. Estetica coerente col resto della pagina.
- **Storico delle valutazioni**: a ogni previsione riuscita, salva in `localStorage`
  (persistente al refresh) **sia gli input usati sia l'esito**. Mostra una lista con
  **data/ora, input usati, esito e probabilità** + un pulsante per **svuotare** lo storico.
  **Cliccando una voce**, ricarica nei campi gli input di quell'analisi (così si può
  ripeterla/modificarla).

### Verifica fase 2
- `python backend/train.py` produce il modello e stampa report+metriche.
- `python backend/app.py` parte; `/health` → modello caricato true.
- Una previsione di prova risponde correttamente; un body incompleto → `400`.
- Apri `frontend/index.html`, compila e invia → risultato; prova input invalidi e backend
  spento → errori gestiti.

> ⛔ **STOP** — Consegna backend + frontend. Aspetta validazione e conferma prima del mobile.

---

## FASE 3 — App mobile (.NET MAUI) — solo se la traccia la richiede

Parti **dopo** l'OK su backend+frontend. Progetto in `mobile/`, target principale
`net10.0-android`. Stesse regole di validazione del frontend.

- **Prerequisiti di build** (da avere installati): .NET 10 SDK, workload `maui`, e per
  Android anche Android SDK + JDK.
- **Calcoli derivati in app** (es. BMI) prima della chiamata.
- Validazione: obbligatori, range, non numerico; **switch** per i booleani.
- Chiamata HTTP al backend via `HttpClient` (`Services/PrevisioneService.cs`). **Base URL**:
  - `http://10.0.2.2:5000` su **Android** (l'emulatore raggiunge l'host così) — `#if ANDROID`;
  - `http://127.0.0.1:5000` altrove.
- **Android**: `android:usesCleartextTraffic="true"` nel manifest (HTTP in chiaro).
- UI con **`Border`** (non `Frame`, deprecato dal .NET 9). Handler eventi con `object?`.
- **Campi numerici** con `Keyboard="Numeric"`. Messaggi d'errore testuali e specifici.
- **Pulsante preset**: carica i 3 preset da `GET /preset` e li inserisce nei campi con un tap.
- **Storico delle valutazioni**: a ogni previsione riuscita, salva in modo persistente
  (`Preferences` o file locale) **sia gli input sia l'esito**: lista con **data/ora,
  input, esito e probabilità** + pulsante per **svuotare** lo storico. **Toccando una
  voce**, ricarica nei campi gli input di quell'analisi.

### Verifica fase 3
- Tieni il **backend avviato**. Build ed esecuzione (Windows è il più rapido, niente emulatore):
  ```bash
  cd mobile
  dotnet build -f net10.0-windows10.0.19041.0 -c Debug -p:WindowsPackageType=None
  ./bin/Debug/net10.0-windows10.0.19041.0/win-x64/<NomeApp>.exe
  ```
  oppure su Android: `dotnet build -t:Run -f net10.0-android`.

> ⛔ **STOP** — Consegna l'app mobile. Aspetta conferma.

---

## FASE 4 — README.md

Ultimo passo. README **breve e pratico** in root, con:

1. **Cosa è** il progetto (1 paragrafo). 2. **Cosa c'è dentro** (cartelle).
3. **Installazione** (venv + `pip install -r requirements.txt`).
4. **Come si usa**: addestrare (`python backend/train.py`), avviare il backend
   (`python backend/app.py`, porta 5000), aprire il frontend (`frontend/index.html`).
5. **App mobile** (se presente): build/esecuzione (Windows e Android), backend avviato,
   indirizzi `10.0.2.2` / `127.0.0.1`.
6. **Come funziona, in breve**: pulizia senza buttare righe, outlier clippati,
   imputazione+scaling dentro la Pipeline (no leakage), modello scelto e perché, backend
   che serve la previsione, frontend che valida e chiama l'API.

---

## Appendice — Accessibilità (frontend e mobile)

- **Label sempre visibile** sopra/accanto a ogni input (il placeholder non basta: sparisce
  quando si digita, contrasto basso). Placeholder solo per esempio/range.
- **Contrasto adeguato**: testo scuro (es. `#2a3b3d`) su sfondo chiaro, WCAG AA (≥ 4.5:1).
- **Niente colore come unico segnale**: esito con testo esplicito, non solo rosso/verde.
- **Tema controllato**: in MAUI forzare `UserAppTheme = AppTheme.Light`.
- **Campi numerici**: `type="number"`/`inputmode` (web), `Keyboard="Numeric"` (MAUI).
- **Messaggi d'errore testuali e specifici** (campo + motivo), vicino all'azione.
- **Target tappabili** adeguati e label associate ai controlli (`<label for>` nel web).
