import streamlit as st
from gtts import gTTS
import io

def visualizza_a_griglia(dati):
    col_sx, col_dx = st.columns(2)
    for indice, riga in enumerate(dati):
        # 1. spacchettiamo TUTTI i dati nell'ordine della query SQL
        id=riga[0]
        parola = riga[1]
        tipo = riga[3]
        definizione = riga[2]
        espressione = riga[4]
        sinonimi = riga[5]
        contrari = riga[6]
        note = riga[7]
        
        # 2. Scegliamo la colonna
        colonna_target = col_sx if indice % 2 == 0 else col_dx
        
        with colonna_target:
            with st.container(border=True):
                st.markdown(f"#### {indice+1} {parola} ({tipo})")
                st.write(f"Definizione: {definizione}")
                if espressione:
                    st.write(f"Espressione: {espressione}")
                if sinonimi:
                    st.write(f"Sinonimi: {sinonimi}")
                if contrari:
                    st.write(f"Contrari: {contrari}")
                if note:
                    st.write(f"{note}")
                # --- AGGIUNTA AUDIO ---
                # Creiamo un buffer di memoria (non salviamo file su disco per velocità)
                if st.button(f"🔊 Ascolta", key=f"btn_audio_{id}"):
                    tts = gTTS(text=parola, lang='en')
                    audio_fp = io.BytesIO()    #Crea un "file virtuale" direttamente nella memoria RAM del server. È temporaneo e velocissimo
                    tts.write_to_fp(audio_fp)  #Non salvare un file MP3 sul disco, scrivi i dati audio direttamente dentro questo oggetto in memoria RAM"
                    st.audio(audio_fp, format='audio/mp3', start_time=0)


# --- QUESTA È LA NUOVA FUNZIONE DI RAGGRUPPAMENTO ---
def visualizza_per_lettera(dati_completi):
    """
    Organizza i vocaboli per lettera alfabetica e mostra sezioni distinte.
    """
    if not dati_completi:
        st.info("Nessun termine trovato.")
        return

    # 1. Creiamo un dizionario per raggruppare: {'A': [...], 'B': [...]}
    gruppi = {}
    
    for riga in dati_completi:
        parola = riga[1]
        
        # Controlla se la parola è None, vuota o solo spazi
        if not parola or str(parola).strip() == "":
            continue  # Salta questo giro del ciclo e passa alla prossima parola
        
        # Prendiamo la prima lettera e la rendiamo maiuscola
        lettera_iniziale = parola[0].upper()

        # Se la lettera è un numero o simbolo, la mettiamo sotto '#'
        if not lettera_iniziale.isalpha():
            lettera_iniziale = "#"
            
        if lettera_iniziale not in gruppi:
            gruppi[lettera_iniziale] = []
        
        gruppi[lettera_iniziale].append(riga)
    
    # 2. Ordiniamo le lettere (A, B, C...)
    lettere_ordinate = sorted(gruppi.keys())
    
    # 3. Ciclo di visualizzazione
    for lettera in lettere_ordinate:
        # Intestazione della lettera (es. "--- A ---")
        st.markdown(f"## 🔤 {lettera}")
        
        # Chiamiamo la funzione griglia SOLO per le parole di questa lettera
        visualizza_a_griglia(gruppi[lettera])
        
        # Spazio vuoto tra una lettera e l'altra
        st.write("") 
        st.write("")