import streamlit as st
from config_db import init_db, aggiungi_parola, leggi_tutto

# --- 2. INTERFACCIA ---
st.set_page_config(page_title="English Dictionary", page_icon="☁️")
st.title("☁️ English Dictionary")

# Inizializza DB all'avvio
try:
    init_db()
except Exception as e:
    st.error(f"Errore di connessione al database: {e}")
    st.stop()

col1, col2 = st.columns([1, 2])
with col1:
    p = st.text_input("Parola")
    t = st.selectbox("Tipo", ["n.m.", "n.f.", "agg.", "v.", "espr."])
with col2:
    d = st.text_area("Definizione")
    e= st.text_input("Espressione")
    s= st.text_input("Sinonimi")
    c= st.text_input("Contrari")
    n= st.text_input("Note")

if st.button("Aggiungi parola"):
    if p and d:
        aggiungi_parola(p, t, d, e, s, c, n)
    else:
        st.warning("Compila i campi!")
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
                st.write(f"Note: {riga[7]}")
else:
    st.info("Database vuoto.")
        
        
