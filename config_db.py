import streamlit as st
import psycopg2

# --- 1. CONFIGURAZIONE DATABASE ---
# Funzione per ottenere la connessione sicura usando i secrets
# @st.cache_resource: Mantiene l'oggetto "connessione" vivo in memoria.
# Non lo ricrea ogni volta che l'app viene ricaricata.
@st.cache_resource
def get_connection():
    db_url = st.secrets["connections"]["neon"]["url"]    # Legge la stringa dal file .streamlit/secrets.toml
    return psycopg2.connect(db_url)

#NON chiudere mai la connessione (togli conn.close())--> rendiamo il tutto più veloce
# Chiudi solo il cursore (cur.close())
def init_db():
    conn = get_connection()  # 1. Chiama la funzione sopra per aprire la linea
    cur = conn.cursor()      # 2. Crea il "Cursore"
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

def aggiungi_parola(parola, tipo, definizione, espressione, sinonimi, contrari, note):
    conn = get_connection() # 1. Apre la connessione
    cur = conn.cursor()     # 2. Chiama il cursore
    try:
        # NOTA: In Postgres si usa %s invece di ?
        cur.execute(
            "INSERT INTO vocaboli (parola, tipo, definizione, espressione, sinonimi, contrari, note) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (parola, tipo, definizione, espressione, sinonimi, contrari, note)
        )
        conn.commit()     # 4. Conferma l'operazione. Senza questo, i dati non vengono salvati davvero.
        st.success(f"Aggiunto al vocabolario: {parola}")
    except psycopg2.errors.UniqueViolation:    # --- GESTIONE DUPLICATI ---
        st.error(f"La parola '{parola}' esiste già nel database!")
        conn.rollback() # Il rollback dice: "Annulla tutto quello che stavi provando a fare e torna pulito".
    except Exception as e:  # --- GESTIONE ALTRI ERRORI ---
        st.error(f"Errore: {e}")
    finally: # Questo blocco viene eseguito SEMPRE, sia in caso di successo che di errore
        cur.close()    # 5. Chiude il cursore

def leggi_tutto():
    conn = get_connection() # 1. Apre la connessione
    cur = conn.cursor()     # 2. Chiama il cursore
    cur.execute('SELECT * FROM vocaboli ORDER BY parola ASC') # 3. Esegue il comando SQL(SELECT * significa "Dammi tutte le colonne";  # FROM vocaboli significa "Dalla tabella vocaboli") 
    dati = cur.fetchall() # # fetchall() ("prendi tutto") li scarica effettivamente e li mette in una lista di tuple
    cur.close()           # 4. Chiude il cursore
    return dati

# 2. CACHE DEI DATI (Data Cache)
# Si ricorda i vocaboli per 5 minuti. Se ricarichi la pagina, legge dalla RAM (0.01s).
@st.cache_data(ttl=300) 
def leggi_tutto_cache():
    conn = get_connection()
    cur = conn.cursor()
    # ... tua query select ...
    cur.execute("SELECT * FROM vocaboli ORDER BY parola ASC")
    dati = cur.fetchall()
    cur.close() 
    # NON chiudere la conn!
    return dati

# IMPORTANTE: Quando aggiungi/elimini una parola, devi "rompere" la cache
def svuota_cache():
    leggi_tutto_cache.clear()

def cerca_vocaboli(testo_ricerca, filtro_tipo=None):
    conn = get_connection() # 1. Apre la connessione
    cur = conn.cursor()     # 2. Chiama il cursore
    
    # Query Base: Cerca sia nella parola che nella definizione
    query = """
        SELECT *
        FROM vocaboli 
        WHERE (parola ILIKE %s OR definizione ILIKE %s)
    """    # ILIKE con % cerca il testo parziale ignorando maiuscole/minuscole
    params = [f"%{testo_ricerca}%", f"%{testo_ricerca}%"]
    
    # Se l'utente ha selezionato dei filtri (es. solo "verbi")
    if filtro_tipo:
        # Aggiungiamo un pezzo alla query SQL
        query += " AND tipo = ANY(%s)"
        params.append(filtro_tipo)
    
    # Ordiniamo alfabeticamente
    query += " ORDER BY parola ASC"
    
    cur.execute(query, tuple(params))
    risultati = cur.fetchall()
    
    cur.close()           # 4. Chiude il cursore
    return risultati

