import streamlit as st

def visualizza_a_griglia(dati):
    col_sx, col_dx = st.columns(2)
    for indice, riga in enumerate(dati):
        # 1. spacchettiamo TUTTI i dati nell'ordine della query SQL
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