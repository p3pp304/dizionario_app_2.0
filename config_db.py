import streamlit as st
import psycopg2

# --- 1. CONFIGURAZIONE DATABASE ---
# Funzione per ottenere la connessione sicura usando i secrets
def get_connection():
    # Legge la stringa dal file .streamlit/secrets.toml
    db_url = st.secrets["connections"]["neon"]["url"]
    return psycopg2.connect(db_url)

def init_db():
    conn = get_connection()  # 1. Chiama la funzione sopra per aprire la linea
    cur = conn.cursor()      # 2. Crea il "Cursore"
    # 3. Esegue il comando SQL (Il progetto di costruzione)
    # Creiamo la tabella se non esiste (Sintassi PostgreSQL)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vocaboli (
            parola TEXT PRIMARY KEY,
            tipo TEXT,
            definizione TEXT
        );
    ''')
    conn.commit()  # 4. Salva le modifiche
    cur.close()    # 5. Chiude il cursore
    conn.close()   # 6. Chiude la connessione

def aggiungi_parola(parola, tipo, definizione, espressione, sinonimi, contrari, note):
    conn = get_connection() # 1. Apre la connessione
    cur = conn.cursor()     # 2. Chiama il cursore
    try:
        # NOTA: In Postgres si usa %s invece di ?
        cur.execute(
            "INSERT INTO vocaboli (parola, tipo, definizione, espressione, sinonimi, contrari, note) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (parola, tipo, definizione, espressione, sinonimi, contrari, note)
        )
        # 4. Conferma l'operazione. Senza questo, i dati non vengono salvati davvero.
        conn.commit()
        st.success(f"Aggiunto su Neon: {parola}")
    except psycopg2.errors.UniqueViolation: # --- GESTIONE DUPLICATI ---
        st.error(f"La parola '{parola}' esiste già nel database!")
        # Quando c'è un errore, la connessione rimane "sporca" o bloccata.
        # Il rollback dice: "Annulla tutto quello che stavi provando a fare e torna pulito".
        conn.rollback() # Importante in Postgres se c'è un errore
    except Exception as e:  # --- GESTIONE ALTRI ERRORI ---
        st.error(f"Errore: {e}")
    finally: # Questo blocco viene eseguito SEMPRE
        conn.close()

def leggi_tutto():
    conn = get_connection() # 1. Apre la connessione
    cur = conn.cursor()     # 2. Chiama il cursore
    cur.execute('SELECT * FROM vocaboli') # 3. Esegue il comando SQL(SELECT * significa "Dammi tutte le colonne";  # FROM vocaboli significa "Dalla tabella vocaboli") 
    dati = cur.fetchall() # # fetchall() ("prendi tutto") li scarica effettivamente e li mette
    conn.close()
    return dati