import streamlit as st

def visualizza_vocaboli(dati):
    if dati:
        for i, riga in enumerate(dati):
            with st.expander(f" {i+1} {riga[1]} ({riga[3]})"):
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
