import google.generativeai as genai # La libreria ufficiale di Google per usare l'AI
import streamlit as st  # Ci serve per leggere i 'secrets' (la password)
import json # Fondamentale: permette a Python di leggere il formato dati standard del web

# Configura Gemini con la chiave dai secrets
def configura_gemini():
    api_key = st.secrets["gemini"]["api_key"]  # 1. Recuperiamo la chiave API dal file nascosto (.streamlit/secrets.toml)
    genai.configure(api_key=api_key)  # 2. Inseriamo la chiave nella libreria. Da ora in poi, siamo autorizzati.

# Se il testo_input è lo stesso, restituisce subito il risultato salvato prima.
@st.cache_data(show_spinner=False)
def analizza_con_gemini(testo_grezzo):
    configura_gemini()
    model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025') # Usiamo il modello veloce ed economico
    
    #--- IL PROMPT (LE ISTRUZIONI) ---
    # Usiamo una f-string (f"...") per inserire il testo dell'utente dentro le istruzioni.
    # Diciamo a Gemini esattamente come formattare i dati
    prompt = f"""
    Sei un assistente lessicografo esperto in Python e informatica.
    Analizza il seguente testo composto da diverse parole in inglese e per ogni parola devi definire tutti campi necessari.    
    Restituisci ESCLUSIVAMENTE una lista JSON valida. Non aggiungere testo prima o dopo, solo il JSON.
    Ogni oggetto nel JSON deve avere queste chiavi esatte:
    - "parola": il termine (in inglese come nel testo o se è in italiano scrivilo in inglese)
    - "tipo": abbreviazione grammaticale ["n.m.", "n.f.", "agg.", "v.", "espr."]
    - "definizione": una definizione chiara e sintetica in italiano, il più delle volte è la traduzione.
    - "sinonimi": (opzionale) una lista di sinonimi separati da virgola in inglese
    - "contrari": (opzionale) una lista di contrari separati da virgola in inglese
    - "espressione": (opzionale) un'espressione idiomatica o frase fatta che include la parola
    - "note": (opzionale) qualsiasi altra informazione rilevante
    Assicurati che il JSON sia ben formattato e valido.
    
    Ecco il testo da analizzare:
    {testo_grezzo}
    """
    
    try:
        response = model.generate_content(prompt) # 1. INVIO: Inviamo il prompt a Google e aspettiamo la risposta.
        testo_risposta = response.text # 2. RICEZIONE: Estraiamo il testo dalla risposta.
        
        # A questo punto 'testo_risposta' è una stringa (testo semplice), non ancora una lista.
        # Esempio di cosa arriva: "```json [ {"parola": "List", ...} ] ```"
        # Questi simboli(```json) mandano in crash la conversione JSON.
        testo_pulito = testo_risposta.replace("```json", "").replace("```", "").strip()
        # Trasformiamo la stringa in una vera lista Python
        dati_json = json.loads(testo_pulito)
        return dati_json
        
    except Exception as e:
        st.error(f"Errore nell'analisi AI: {e}")
        return [] # invece di far crashare l'app, mostriamo l'errore e restituiamo una lista vuota.
    

""" LISTA CAMPPI RICHIESTI:
- models/gemini-2.5-flash-image
- models/gemini-2.5-flash-preview-09-2025
- models/gemini-2.5-flash-lite-preview-09-2025
- models/gemini-3-pro-preview
- models/gemini-3-pro-image-preview
- models/nano-banana-pro-preview
- models/gemini-robotics-er-1.5-preview
- models/gemini-2.5-computer-use-preview-10-2025 """