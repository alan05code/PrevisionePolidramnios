"""Backend Flask: espone la previsione del Polidramnios.

Endpoint:
- GET  /health      -> stato del servizio e se il modello è caricato
- POST /previsione  -> body JSON con le 8 feature, risponde con previsione e probabilità

Uso:  python app.py   (oppure: flask --app app run)
"""
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import ColonneFeatures
from predizione_utils import CaricaModello, PrevediPolidramnios

app = Flask(__name__)
CORS(app)  # consente le chiamate dal frontend (origine diversa)

# Il modello viene caricato una sola volta all'avvio (non a ogni richiesta).
try:
    PACCHETTO = CaricaModello()
except FileNotFoundError as e:
    PACCHETTO = None
    print("ATTENZIONE:", e)


@app.get("/health")
def health():
    return jsonify({"stato": "ok", "modello_caricato": PACCHETTO is not None})


@app.post("/previsione")
def previsione():
    if PACCHETTO is None:
        return jsonify({"errore": "Modello non disponibile. Esegui prima il training."}), 503

    corpo = request.get_json(silent=True) or {}
    try:
        # Validazione al confine: tutte le feature presenti e convertibili a float.
        dati = {c: float(corpo[c]) for c in ColonneFeatures}
        risultato = PrevediPolidramnios(dati, PACCHETTO)
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"errore": f"Input non valido: {e}",
                        "feature_richieste": ColonneFeatures}), 400

    return jsonify(risultato)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
