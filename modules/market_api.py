import yfinance as yf

def get_current_price(ticker: str):
    """
        Recupera il prezzo corrente di qualsiasi strumento Yhaoo Finance
    - restituisce il prezzo come float, oppure None se non disponibile
    """
    try:
        # creazione oggetto ticker yfinance per strumento richiesto
        stock = yf.Ticker(ticker.upper())

        # fast_info è più veloce di info() — contiene solo i dati essenziali
        price = stock.fast_info["last_price"]

        # se il prezzo è None o 0 il fato non è disp
        if not price:
            print(f"Prezzo non disponibile per {ticker}")
            return None
        
        return round(price, 4)
    
    except Exception as e:
        # catturo qualsiasi errore di rete o yfinance
        print(f" X errore nel recupero del prezzo per {ticker}: {e}")
        return None
    
def get_all_prices(tickers: str):
    """Recupera i prezzi correnti di una lista di ticker in una sola chiamata.
    - tickers: lista di ticker es. ['VWCE.MI', 'GOLD.MI', 'WBIT.DE', 'XEON.MI']
    - restituisce un dizionario es. {'VWCE.MI': 161.61, 'GOLD.MI': 45.23, ...}
    """
    prices = {}

    for ticker in tickers:
        # recupero il prezzo per ogni tocker usando get_current_price
        price = get_current_price(ticker)

        #aggiungo al dict se il prezzo è disp
        if price is not None:
            prices[ticker.upper()] = price
        else:
            prices[ticker.upper()] = None

    return prices

# fun gestione errori

def validate_ticker(ticker):
    """
    Verifica che un ticker esista su Yahoo Finance prima di aggiungerlo al portafoglio.
    - ticker: es. 'VWCE.MI'
    - restituisce True se il ticker esiste, False altrimenti
    """
    try:
        stock = yf.Ticker(ticker.upper())
        price = stock.fast_info["last_price"]

        # se il prezzo è 0 o None il ticker non è vlido
        if not price:
            return False
        
        return True
    except Exception:
        return False