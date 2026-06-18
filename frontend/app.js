"use strict";

const API = "http://127.0.0.1:5000";

// Per ogni campo numerico: id input -> [nome feature backend, min, max, etichetta]
const CAMPI = {
  eta:        ["Eta_anni", 14, 55, "Età"],
  gravidanze: ["Numero_Gravidanze_Pregresse", 0, 20, "Gravidanze pregresse"],
  cesarei:    ["Numero_Tagli_Cesarei_Pregressi", 0, 12, "Tagli cesarei pregressi"],
  pressione:  ["Pressione_Diastolica_mmHg", 40, 130, "Pressione diastolica"],
  insulina:   ["Insulina_Sierica_2ore", 0, 400, "Insulina sierica"],
};

const form = document.getElementById("form");
const bmiOut = document.getElementById("bmi");
const errBox = document.getElementById("errore");
const risultato = document.getElementById("risultato");

// --- Calcolo BMI live da altezza (cm) e peso (kg) -------------------------------
function calcolaBMI() {
  const h = parseFloat(document.getElementById("altezza").value);
  const w = parseFloat(document.getElementById("peso").value);
  if (!isFinite(h) || !isFinite(w) || h <= 0 || w <= 0) {
    bmiOut.value = "";
    return null;
  }
  const bmi = w / Math.pow(h / 100, 2);
  bmiOut.value = bmi.toFixed(1);
  return bmi;
}
document.getElementById("altezza").addEventListener("input", calcolaBMI);
document.getElementById("peso").addEventListener("input", calcolaBMI);

// --- Helpers --------------------------------------------------------------------
function mostraErrore(msg) {
  errBox.textContent = msg;
  errBox.classList.remove("d-none");
  risultato.classList.add("d-none");
}

// Legge un campo numerico: obbligatorio, numerico, dentro il range.
function leggiNumero(id, min, max, etichetta, errori) {
  const v = document.getElementById(id).value.trim();
  if (v === "") { errori.push(`${etichetta}: campo obbligatorio`); return null; }
  const n = Number(v);
  if (!isFinite(n)) { errori.push(`${etichetta}: valore non numerico`); return null; }
  if (n < min || n > max) { errori.push(`${etichetta}: fuori range (${min}–${max})`); return null; }
  return n;
}

// --- Invio ----------------------------------------------------------------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errBox.classList.add("d-none");

  const errori = [];
  const dati = {};

  // Campi numerici diretti
  for (const id in CAMPI) {
    const [nome, min, max, etichetta] = CAMPI[id];
    const n = leggiNumero(id, min, max, etichetta, errori);
    if (n !== null) dati[nome] = n;
  }

  // Altezza e peso (servono solo per il BMI)
  const altezza = leggiNumero("altezza", 120, 220, "Altezza", errori);
  const peso = leggiNumero("peso", 30, 250, "Peso", errori);
  const bmi = calcolaBMI();
  if (altezza !== null && peso !== null) {
    if (bmi === null || bmi < 14 || bmi > 60) {
      errori.push("Indice di Massa Corporea fuori range (14–60): controlla altezza e peso");
    } else {
      dati["Indice_Massa_Corporea"] = Number(bmi.toFixed(1));
    }
  }

  // Coerenza logica: i cesarei non possono superare le gravidanze
  if (dati["Numero_Tagli_Cesarei_Pregressi"] > dati["Numero_Gravidanze_Pregresse"]) {
    errori.push("I tagli cesarei non possono superare le gravidanze pregresse");
  }

  // Checkbox -> 0/1
  dati["Diabete_Gestazionale"] = document.getElementById("diabeteGest").checked ? 1 : 0;
  dati["Diabete_Pregravidico"] = document.getElementById("diabetePreg").checked ? 1 : 0;

  if (errori.length) { mostraErrore(errori.join(" • ")); return; }

  // Chiamata al backend con gestione errori
  const btn = document.getElementById("invia");
  btn.disabled = true;
  try {
    const resp = await fetch(API + "/previsione", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dati),
    });
    const json = await resp.json();
    if (!resp.ok) { mostraErrore(json.errore || "Errore dal server"); return; }
    mostraRisultato(json);
  } catch (err) {
    mostraErrore("Impossibile contattare il server. Verifica che il backend sia attivo (porta 5000).");
  } finally {
    btn.disabled = false;
  }
});

// --- Risultato ------------------------------------------------------------------
function mostraRisultato(json) {
  const perc = Math.round(json.probabilita * 100);
  const positivo = json.previsione === 1;

  const esito = document.getElementById("esito");
  esito.textContent = positivo ? "Rischio di Polidramnios" : "Nessun rischio rilevato";
  esito.className = "fs-3 fw-bold mb-3 " + (positivo ? "esito-positivo" : "esito-negativo");

  const barra = document.getElementById("barra");
  barra.style.width = perc + "%";
  barra.className = "progress-bar " + (positivo ? "barra-positivo" : "barra-negativo");

  document.getElementById("prob").textContent = perc + "%";
  risultato.classList.remove("d-none");
  errBox.classList.add("d-none");
}