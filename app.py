import streamlit as st
from config_db import init_db, aggiungi_parola, leggi_tutto, cerca_vocaboli
from ai_tools import analizza_con_gemini
from view import visualizza_vocaboli        

# --- 1. FUNZIONE POP-UP SALVATAGGIO CON PASSWORD ---
@st.dialog("🔐 Conferma Salvataggio") #@ (decoratore) trasforma la funzione che c'è sotto in un pop-up che oscura il resto della pagina
def pop_up_salvataggio(dati_da_salvare):
    st.write(f"Stai per aggiungere **{len(dati_da_salvare)}** nuovi termini al database.")
    st.warning("Questa operazione è definitiva.")

    # Input password dentro il pop-up
    password = st.text_input("Inserisci Password", type="password")
    
    if st.button("Conferma", type="primary"):
        if password == st.secrets["admin"]["password"]:
            
            # --- LOGICA DI SALVATAGGIO ---
            progress_bar = st.progress(0)
            total = len(dati_da_salvare)

            for i, item in enumerate(dati_da_salvare):
                aggiungi_parola(
                    item['parola'], 
                    item['tipo'], 
                    item['definizione'],
                    item.get('espressione', ''), 
                    item.get('sinonimi', ''),
                    item.get('contrari', ''),
                    item.get('note', '')
                )
                progress_bar.progress((i + 1) / total)
            
            st.success("✅ Salvataggio completato!")
            
            # Pulizia e Riavvio
            st.session_state.risultati_ai = None
            st.rerun()
            
        else:
            st.error("❌ Password errata.")


# --- 2. INTERFACCIA ---
st.set_page_config(page_title="English Dictionary", page_icon="☁️")
st.title("☁️ English Dictionary")

# Inizializza DB all'avvio
try:
    init_db()
except Exception as e:
    st.error(f"Errore di connessione al database: {e}")
    st.stop()

# ---- TABS PER I DUE MODI DI INSERIMENTO
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
            st.session_state.risultati_ai,  # Passiamo la lista direttamente
            num_rows="dynamic",
            use_container_width=True,
            # Nota: column_config funziona anche con le liste!
            column_config={
                "parola": st.column_config.TextColumn("Termine", required=True),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=["n.m.", "n.f.", "v.", "agg.", "espr."], required=True),
                "definizione": st.column_config.TextColumn("📖 Definizione", width="large", required=True)
            },
            hide_index=True
        )
        
        
        # 5. SALVATAGGIO NEL DATABASE
        col_save, col_discard = st.columns([2, 4])
        with col_save:
            # IL NUOVO BOTTONE SEMPLICE
            # Quando lo clicchi, apre la funzione pop-up definita sopra
            if st.button("💾 Salva tutto nel Database", use_container_width=True):
                if len(dati_modificati) > 0:
                    pop_up_salvataggio(dati_modificati)
                else:
                    st.warning("La tabella è vuota!")

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

# 1. BARRA DI RICERCA E FILTRI
# Usiamo le colonne per mettere tutto sulla stessa riga
col_search, col_filter = st.columns([3, 1])

with col_search:
    # Input di ricerca principale
    search_text = st.text_input("Inserisci la parola da cercare", placeholder="Es. Funzioni, Liste, Cicli...")

with col_filter:
    # Filtro Multiplo per Tipo
    tipi_selezionati = st.multiselect(
        "Filtra per:", 
        ["n.m.", "n.f.", "v.", "agg.", "code", "espr."],
        placeholder="Tutti i tipi"
    )

# 2. LOGICA DI RICERCA
# Se la barra è vuota, mostriamo tutto? O niente? 
# Di solito è meglio mostrare tutto o gli ultimi aggiunti.
# Qui usiamo la funzione creata prima:

dati_s = cerca_vocaboli(search_text, tipi_selezionati)

# 3. VISUALIZZAZIONE RISULTATI (Dashboard Style)
if not dati_s:
    st.info("Nessun termine trovato. Prova a cercare qualcos'altro!")
else:
    st.write(f"Trovati **{len(dati_s)}** termini.")
    dati = dati_s
    
visualizza_vocaboli(dati)
        
        
