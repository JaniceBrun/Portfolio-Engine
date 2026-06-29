"""Database manager"""

#sezione import

import sqlite3
from datetime import date
import threading # impedisce scritture simultanee e evita dblock

#definizione variabili

db_lock = threading.Lock()
DB_PATH = "db/portfolio.db"


# Funzione setup

def get_connection():
    """restituisce una connessione al db sqlite"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON") # abilito vincoli fk in sqlite
    conn.execute("PRAGMA journal_mode=WAL;") # per letture parallele, scritt veloci e meno lock
    return conn


# creazione tabelle sqlite

def init_db():
    """Crea le tabelle se non esistono già"""
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker   TEXT NOT NULL UNIQUE,
                name     TEXT NOT NULL,
                type     TEXT NOT NULL CHECK (type IN('etf', 'etc', 'etn', 'azione', 'obbligazione', 'crypto')),
                currency TEXT NOT NULL DEFAULT 'EUR'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id     INTEGER NOT NULL REFERENCES positions(id),
                quantity        REAL    NOT NULL CHECK(quantity > 0),
                price           REAL    NOT NULL CHECK(price > 0),
                purchased_on    TEXT    NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id     INTEGER NOT NULL REFERENCES positions(id),
                price           REAL    NOT NULL,
                recorded_on     TEXT    NOT NULL
            )  
        """)

        conn.commit()
        conn.close()

# funzioni operative

def add_position(ticker: str, name, type_, currency="EUR"):
    """Inserisce un nuovo strumento nel pf"""
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO positions ( ticker, name, type, currency)
            VALUES (?, ?, ?, ?)
        """, (ticker.upper(), name, type_, currency))
        position_id = cursor.lastrowid
        conn.commit()
        conn.close()
    return position_id

def add_or_update_position(ticker: str, name, type_, quantity, price, currency="EUR"):
    """
    Se la posizione esiste, aggiunge un acquisto.
    Se non esiste, la crea e poi aggiunge l'acquisto.
    """
    ticker = ticker.upper()

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # Cerca se esiste già
        cursor.execute("SELECT id FROM positions WHERE ticker = ?", (ticker,))
        row = cursor.fetchone()

        if row:
            # Esiste → aggiungo acquisto
            position_id = row["id"]
        else:
            # Non esiste → creo posizione
            cursor.execute("""
                INSERT INTO positions (ticker, name, type, currency)
                VALUES (?, ?, ?, ?)
            """, (ticker, name, type_, currency))
            position_id = cursor.lastrowid

        # Aggiungo l'acquisto
        cursor.execute("""
            INSERT INTO purchases (position_id, quantity, price, purchased_on)
            VALUES (?, ?, ?, ?)
        """, (position_id, quantity, price, str(date.today())))

        conn.commit()
        conn.close()

    return position_id


def add_purchase(position_id, quantity, price, purchased_on=None):
    """
    Inserisce un acquisto nella tabella purchases.
    -position_id : id della posizione a cui appartiene l'acquisto
    -quantity: numero di quote acquistato
    -price: prezzo unitario pagato
    -purchased_on: data acquisto in formato YYYY-MM-DD (default:oggi)
    """
    # se non viene passata una data una la data di oggi
    if purchased_on is None:
        purchased_on = str(date.today())

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        #inserisce il record nella tabella purchases
        cursor.execute("""
            INSERT INTO purchases (position_id, quantity, price, purchased_on)
            VALUES (?, ?, ?, ?)
        """, (position_id, quantity, price, purchased_on))

        conn.commit()
        conn.close()

def get_position_by_ticker(ticker):
    """
    Crea una posizione nel db tramite ticker.
    restituisce il record come dizionario, oppure None se non esiste.
    - ticker: es. 'VWCE.MI'
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # cerca la posizione con il tcker specificato(upper() per sicurezza)
        cursor.execute("""
            SELECT * FROM positions WHERE ticker = ?
        """, (ticker.upper(),))

        row = cursor.fetchone()
        conn.close()

    #fetchone() restituisce None se non trova nulla
    return dict(row) if row else None

def get_all_positions():
    """
    restituisce titte le posizioni presenti nel portafoglio
    come lista di dizionare, ordinate per tipo e ticker.
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # recupera tutte le righe della tabella positions
        cursor.execute("""
            SELECT * FROM positions ORDER BY type, ticker
        """)

        rows = cursor.fetchall()
        conn.close()

    #converte ogni riga in dizionario, restituisce lista vuote se non ci sono posizioni
    return [dict(row) for row in rows]

def get_position_summary(position_id):
    """
    Calcola il riepilogo aggregato di una posizione a partire dagli acquisti.
    Restituisce un dizionario con:
    - total_quantity: numero totale di quote possedute
    - avg_price: prezzo medio di carico ponderato
    - total_cost: capitale totale investito
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # calcola quantità totale, prezzo medio ponderato e costo totale
        # direttamente in SQL senza caricare tutti gli acquisti in memoria
        cursor.execute("""
            SELECT
                SUM(quantity)                        AS total_quantity,
                SUM(quantity * price) / SUM(quantity) AS avg_price,
                SUM(quantity * price)                AS total_cost
            FROM purchases
            WHERE position_id = ?
        """, (position_id,))

        row = cursor.fetchone()
        conn.close()

    # se non esistono acquisti per questa posizione restituisce None
    return dict(row) if row and row["total_quantity"] else None


def remove_position(ticker):
    """
    Rimuove una posizione e tutti i suoi acquisti dal database.
    Restituisce True se la posizione esisteva, False se non trovata.
    - ticker: es. 'VWCE.MI'
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # cerca prima la posizione per verificare che esista
        cursor.execute("""
            SELECT id FROM positions WHERE ticker = ?
        """, (ticker.upper(),))

        row = cursor.fetchone()

        # se non esiste restituisce False senza fare nulla
        if row is None:
            conn.close()
            return False

        position_id = row["id"]

        # elimina prima gli acquisti collegati (rispetta il vincolo FK)
        cursor.execute("""
            DELETE FROM purchases WHERE position_id = ?
        """, (position_id,))

        # elimina poi lo storico prezzi collegato
        cursor.execute("""
            DELETE FROM price_history WHERE position_id = ?
        """, (position_id,))

        # infine elimina la posizione
        cursor.execute("""
            DELETE FROM positions WHERE id = ?
        """, (position_id,))

        conn.commit()
        conn.close()
    return True

def update_purchase(position_id, quantity, price, purchased_on=None):
    """
    Aggiunge un nuovo acquisto a una posizione esistente.
    Usata quando si acquistano nuove quote di uno strumento già in portafoglio.
    - position_id: id della posizione a cui aggiungere l'acquisto
    - quantity: numero di quote del nuovo acquisto
    - price: prezzo unitario del nuovo acquisto
    - purchased_on: data acquisto in formato YYYY-MM-DD (default: oggi)
    """
    # se non viene passata una data usa la data di oggi
    if purchased_on is None:
        purchased_on = str(date.today())

    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # inserisce il nuovo acquisto nella tabella purchases
        cursor.execute("""
            INSERT INTO purchases (position_id, quantity, price, purchased_on)
            VALUES (?, ?, ?, ?)
        """, (position_id, quantity, price, purchased_on))

        conn.commit()
        conn.close()


def add_price_snapshot(position_id, price):
    """
    Salva il prezzo corrente di mercato nella tabella price_history.
    Viene chiamata ogni volta che si aggiornano i prezzi da yfinance.
    - position_id: id della posizione
    - price: prezzo corrente recuperato da yfinance
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # inserisce il prezzo con la data di oggi
        cursor.execute("""
            INSERT INTO price_history (position_id, price, recorded_on)
            VALUES (?, ?, ?)
        """, (position_id, price, str(date.today())))

        conn.commit()
        conn.close()


def get_latest_price(position_id):
    """
    Recupera l'ultimo prezzo salvato in price_history per una posizione.
    Restituisce il record come dizionario, oppure None se non ci sono prezzi salvati.
    - position_id: id della posizione
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # ORDER BY recorded_on DESC + LIMIT 1 = prende solo il più recente
        cursor.execute("""
            SELECT price, recorded_on FROM price_history
            WHERE position_id = ?
            ORDER BY recorded_on DESC
            LIMIT 1
        """, (position_id,))

        row = cursor.fetchone()
        conn.close()

    return dict(row) if row else None

# funzione per recuperare un prezzo piu vicino alla data indicata(per calcolo delta)
def get_price_by_date(position_id, date):
    """
    Recupera il prezzo salvato in price_history per una data specifica.
    - position_id: id della posizione
    - date: data in formato YYYY-MM-DD
    - restituisce il record come dizionario, oppure None se non trovato
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        # cerca il prezzo più vicino alla data richiesta
        # ORDER BY ABS permette di trovare il record più vicino
        # nel caso non ci sia un record esatto per quella data
        cursor.execute("""
            SELECT price, recorded_on FROM price_history
            WHERE position_id = ?
            AND recorded_on <= ?
            ORDER BY recorded_on DESC
            LIMIT 1
        """, (position_id, date))

        row = cursor.fetchone()
        conn.close()

    return dict(row) if row else None

#funzione per recupre prezzi di una posizione per calcolare history
def get_price_history(position_id, from_date=None, to_date=None):
    """
    Recupera lo storico dei prezzi per una posizione.
    - position_id: id della posizione
    - from_date: data minima (YYYY-MM-DD) opzionale
    - to_date: data massima (YYYY-MM-DD) opzionale
    - restituisce una lista di dict: [{"recorded_on": "...", "price": ...}, ...]    
    """
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT recorded_on, price
            FROM price_history
            WHERE position_id = ?
        """
        params = [position_id]

        if from_date:
            query += " AND recorded_on >= ? "
            params.append(from_date)

        if to_date:
            query += " And recorded_on <= ?"
            params.append(to_date)

        query += " ORDER BY recorded_on ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

    return [dict(row) for row in rows]





