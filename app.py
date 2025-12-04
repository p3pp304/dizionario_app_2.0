import streamlit as st
from config_db import init_db, aggiungi_parola, leggi_tutto
from ai_tools import analizza_con_gemini


# --- 2. INTERFACCIA ---
st.set_page_config(page_title="English Dictionary", page_icon="☁️")
st.title("☁️ English Dictionary")

# Inizializza DB all'avvio
try:
    init_db()
except Exception as e:
    st.error(f"Errore di connessione al database: {e}")
    st.stop()

tab_ai, tab_man = st.tabs(["Aggiungi lista di parole con AI", "Aggiungi parola manualmente"])

# 1. MODO AI (La novità!)
with tab_ai:
    # 1. ISTRUZIONI E INPUT
    st.markdown(f"Incolla un testo grezzo, appunti o una lista disordinata.\n Gemini la formatterà per te.")
    testo_input = st.text_area("Incolla qui i tuoi appunti:", height=200, placeholder="Inserisci le parole che non conosci...")
    
    # 2. GESTIONE DELLA MEMORIA (SESSION STATE)
    if "risultati_ai" not in st.session_state: # Qui controlliamo: "Esiste già un cassetto per i risultati? Se no, crealo vuoto."
        st.session_state.risultati_ai = None  # Variabile di stato (memoria a lungo termine della sessione di lavoro) per salvare i risultati temporanei

    # 3. IL PULSANTE DI ANALISI (CHIAMATA API)
    if st.button("✨ Analizza e Estrai"):
        with st.spinner("Gemini sta leggendo i tuoi appunti..."):
            st.session_state.risultati_ai = analizza_con_gemini(testo_input)  # e SALVIAMO IL RISULTATO NELLA MEMORIA DI SESSIONE, non in una variabile normale.
    
    # 4. VISUALIZZAZIONE RISULTATI (ANTEPRIMA). Se abbiamo risultati dall'AI, mostriamo un'anteprima
    if st.session_state.risultati_ai:
        st.success(f"Trovati {len(st.session_state.risultati_ai)} termini!")
        st.info("👇 Puoi modificare i dati direttamente nella tabella qui sotto prima di salvare!")

        # st.data_editor crea una tabella interattiva (come Excel).
        # num_rows="dynamic" ti permette anche di AGGIUNGERE o CANCELLARE righe!
        dati_modificati = st.data_editor(
            st.session_state.risultati_ai, 
            num_rows="dynamic",
            use_container_width=True
        )
        
        # 5. SALVATAGGIO NEL DATABASE
        col_save, col_discard = st.columns([1, 4])
        with col_save:
            if st.button("💾 Conferma e Salva Tutto"):
                # Creiamo una barra di progresso (parte da 0%)
                progress_bar = st.progress(0)
                total = len(dati_modificati)

                # Ciclo FOR per salvare ogni singola parola trovata. enumerate(lista) ci dà sia l'indice (i) che l'oggetto (item)
                for i, item in enumerate(dati_modificati):
                    # Salviamo nel DB uno per uno
                    aggiungi_parola(item['parola'], item['tipo'], item['definizione'], 
                                   item.get('espressione', ''), item.get('sinonimi', ''), item.get('contrari', ''), item.get('note', ''))
                    progress_bar.progress((i + 1) / total)  # Aggiorna la barra di progresso

                st.success("Tutti i termini sono stati salvati")
                st.session_state.risultati_ai = None # Reset
                st.rerun()

#INSERIMENTO MANUALE PAROLA            
with tab_man:
    
    st.caption("Inserisci una nuova parola nel dizionario.")
    col1, col2 = st.columns([4, 1])
    with col1:
        p = st.text_input("Parola")
    with col2:
        t = st.selectbox("Tipo", ["n.m.", "n.f.", "agg.", "v.", "espr."])

    d = st.text_area("Definizione")

    st.markdown("Dettagli opzionali")
    col3, col4 = st.columns([1, 1])
    with col3:
        s= st.text_input("Sinonimi")
        e= st.text_area("Espressione")
    with col4:
        c= st.text_input("Contrari")
        n= st.text_area("Note")

    if st.button("Aggiungi parola"):
        if p and d:
            aggiungi_parola(p, t, d, e, s, c, n)
        else:
            st.warning("Compila i campi!")

# 2. VISUALIZZA IL DATABASE
st.markdown("Vocabulary")
dati = leggi_tutto()
if dati:
    for riga in dati:
        with st.expander(f"{riga[0]} {riga[1]} ({riga[3]})"):
            st.write(f"Definizione: {riga[2]}")
            if riga[4]:
                st.write(f"Espressione: {riga[4]}")
            if riga[5]:
                st.write(f"Sinonimi: {riga[5]}")
            if riga[6]:
                st.write(f"Contrari: {riga[6]}")
            if riga[7]:
                st.write(f"{riga[7]}")
else:
    st.info("Database vuoto.")
        
        
