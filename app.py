import streamlit as st
from config_db import init_db, aggiungi_parola, leggi_tutto

# --- 2. INTERFACCIA ---
st.set_page_config(page_title="English Dictionary", page_icon="☁️")
st.title("☁️ English Dictionary Cloud")

# Inizializza DB all'avvio
try:
    init_db()
except Exception as e:
    st.error(f"Errore di connessione al database: {e}")
    st.stop()

# TABS
tab1, tab2 = st.tabs(["📝 Aggiungi", "🔍 Cerca"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        p = st.text_input("Parola")
        t = st.selectbox("Tipo", ["n.m.", "n.f.", "agg.", "v.", "espr."])
    with col2:
        d = st.text_area("Definizione")
        
    if st.button("Salva in Cloud"):
        if p and d:
            aggiungi_parola(p, t, d)
        else:
            st.warning("Compila i campi!")

with tab2:
    st.markdown("### Dati dal Cloud")
    dati = leggi_tutto()
    if dati:
        for riga in dati:
            with st.expander(f"{riga[0]} ({riga[1]})"):
                st.write(riga[2])
    else:
        st.info("Database vuoto.")
        
        
