import streamlit as st

# Questo crea un titolo grande
st.title("ENGLISH VOCABULARY")

# Questo scrive del testo normale
st.write("Benvenuto! Qui raccoglieremo le parole nuove.")

# Crea una casella di testo dove l'utente può scrivere
nuova_parola = st.text_input("Inserisci una nuova parola:")

# Possiamo subito reagire a quello che l'utente scrive
if nuova_parola:
    st.write(f"Hai scritto: {nuova_parola}")

# Mette un titolo nella barra laterale a sinistra
st.sidebar.title("Menu")