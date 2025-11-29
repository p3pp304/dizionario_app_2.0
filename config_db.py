import streamlit as st
import psycopg2

# --- 1. CONFIGURAZIONE DATABASE ---
# Funzione per ottenere la connessione sicura usando i secrets
def get_connection():
    # Legge la stringa dal file .streamlit/secrets.toml
    db_url = st.secrets["connections"]["neon"]["url"]
    return psycopg2.connect(db_url)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Creiamo la tabella se non esiste (Sintassi PostgreSQL)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vocaboli (
            parola TEXT PRIMARY KEY,
            tipo TEXT,
            definizione TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def aggiungi_parola(parola, tipo, definizione):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # NOTA: In Postgres si usa %s invece di ?
        cur.execute(
            "INSERT INTO vocaboli (parola, tipo, definizione) VALUES (%s, %s, %s)",
            (parola, tipo, definizione)
        )
        conn.commit()
        st.success(f"Aggiunto su Neon: {parola}")
    except psycopg2.errors.UniqueViolation:
        st.error(f"La parola '{parola}' esiste già nel database!")
        conn.rollback() # Importante in Postgres se c'è un errore
    except Exception as e:
        st.error(f"Errore: {e}")
    finally:
        conn.close()

def leggi_tutto():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM vocaboli')
    dati = cur.fetchall()
    conn.close()
    return dati