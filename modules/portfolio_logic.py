#import funzioni necessarie
from db.db_manager import (
    get_all_positions,
    get_position_summary,
    get_latest_price,
    add_price_snapshot,
    get_position_by_ticker,
    get_price_by_date
)
from modules.market_api import get_all_prices

# fun che riceva dati grezzo e restituisce  un dict con tutti i valori per unaposizione
# valore attuale, p/l e delta

def calculate_position(position, summary, current_price, previous_price=None, previous_date=None):
    """
    Calcola tutti i valori economici di una singola posizione.
    - position: dizionario con i dati statici da positions
    - summary: dizionario con total_quantity, avg_price, total_cost da purchases
    - current_price: prezzo corrente da yfinance
    - previous_price: ultimo prezzo salvato in price_history (opzionale)
    - previous_date: data a cui si riferisce il previous_price (opzionale, solo per info)
    - restituisce un dizionario con tutti i valori calcolati
    """
    # dati base
    quantity    = summary["total_quantity"]
    avg_price   = summary["avg_price"]
    total_cost  = summary["total_cost"]

    # calcolo valore attuale
    current_value = round(current_price * quantity, 2)

    # calcolo P/L assoluto e percentuale
    pl_abs  = round(current_value - total_cost, 2)
    pl_pct  = round((pl_abs / total_cost) * 100, 2)

    # calcolo delta rispetto all'ultimo prezzo salvato
    if previous_price and previous_price > 0:
        delta_abs = round(current_price - previous_price, 4)
        delta_pct = round((delta_abs / previous_price) * 100, 2)
    else:
        #nessun prezzo precendente disp
        delta_abs = None
        delta_pct = None

    return {
        "id":             position["id"],
        "ticker":         position["ticker"],
        "name":           position["name"],
        "type":           position["type"],
        "quantity":       quantity,
        "avg_price":      round(avg_price, 4),
        "total_cost":     round(total_cost, 2),
        "current_price":  current_price,
        "current_value":  current_value,
        "pl_abs":         pl_abs,
        "pl_pct":         pl_pct,
        "delta_abs":      delta_abs,
        "delta_pct":      delta_pct,
        "previous_date":  previous_date,        
    }


#funzione accessoria per decidere che prezzo prece usare per il delta
# usa get_price_by_date() o get_latest_prices()

def get_previous_price(position_id, reference_date=None):
    """
    Recupera il prezzo precedente per il calcolo del delta.
    - usa get_price_by_date se reference_date è specificata
    - altrimenti usa get_latest_price
    """
    if reference_date:
        return get_price_by_date(position_id, reference_date)
    return get_latest_price(position_id)


# fun per costruzione risultato sotto forma di dict per una  posizione, None se dati non disp
# richiama get_previous_prive() e calculate_position()

def build_position_result(position, current_prices, reference_date=None):
    """
    Costruisce il dizionario risultato per una singola posizione.
    - position: dizionario con i dati statici da positions
    - current_prices: dizionario ticker → prezzo corrente
    - reference_date: data per calcolo delta (opzionale)
    - restituisce None se i dati non sono disponibili
    """
    ticker      = position["ticker"]
    position_id = position["id"]

    # verific0 disponibilità prezzo
    if current_prices.get(ticker) is None:
        print(f"prezzo non disponibile per {ticker}, posizione saltata")
        return None

    # recupero riepilogo acquisti
    summary = get_position_summary(position_id)
    if not summary:
        return None

    # recupero prezzo precedente per il delta
    prev = get_previous_price(position_id, reference_date)
    previous_price = prev["price"] if prev else None
    previous_date  = prev["recorded_on"] if prev else None

    return calculate_position(
        position = position,
        summary = summary,
        current_price = current_prices[ticker],
        previous_price = previous_price,
        previous_date = previous_date
    )


# recupera tutti i dati e restituisce la lista completa delle pos calcolate
#richiama get_all_positions() get_all_pricies() build_position_results()

def get_portfolio_data( reference_date=None):
    """
    Recupera i dati statici dal db e i prezzi aggiornati da yfinance.
    - reference_date: data per calcolo delta in formato YYYY-MM-DD (opzionale)
    - restituisce una lista di dizionari con tutti i valori calcolati per ogni posizione    
    """
    positions = get_all_positions()
 
    if not positions:
        return []
    
    #rec tutti i prezzi in una sola chiamata yfinance
    tickers = [p["ticker"] for p in positions]
    current_prices = get_all_prices(tickers)

    # DEBUG
    # print(f"DEBUG: tickers = {tickers}")
    # print(f"DEBUG: current_prices = {current_prices}")

    results = []

    for position in positions:
        calc = build_position_result(position, current_prices, reference_date)
        if calc:
            results.append(calc)

    return results


# funzione calcolo totali e weight

def calculate_totals(results):
    """
    Calcola i totali del portafoglio e il peso % di ogni posizione.
    - results: lista di posizioni già calcolate da get_portfolio_data()
    - restituisce un dizionario con i totali del portafoglio
    """
    if not results:
        return {
            "total_value": 0.0,
            "total_cost": 0.0,
            "pl_total_abs": 0.0,
            "pl_total_pct": 0.0,
        }            

    total_value = sum(r["current_value"] for r in results)
    total_cost  = sum(r["total_cost"]    for r in results)

    # calcola il peso % di ogni posizione sul totale
    # fatto qui perché ci serve il total_value completo
    for r in results:
        r["weight_pct"] = round((r["current_value"] / total_value) * 100, 2) if total_value > 0 else 0

    pl_total_abs = round(total_value - total_cost, 2)
    pl_total_pct = round((pl_total_abs / total_cost) * 100, 2) if total_cost > 0 else 0

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "pl_total_abs": pl_total_abs,
        "pl_total_pct": pl_total_pct,
    }


# riceve lista di posizioni gia calcolare e le filta per categoria e valore min
def apply_filters(results, filter_type=None, filter_min_value=None):
    """
    Applica filtri per categoria e/o valore minimo a una lista di posizioni.
    - results: lista di posizioni calcolate
    - filter_type: es. 'etf', 'etc', 'etn' (opzionale)
    - filter_min_value: valore minimo in EUR (opzionale)
    - restituisce la lista filtrata
    """
    if filter_type:
        results = [r for r in results if r["type"] == filter_type.lower()]

    if filter_min_value:
        results = [r for r in results if r["current_value"] >= filter_min_value]

    return results


# funzione che funge da orchestratore principale, restituisce pos filtrate e tot

def calculate_portfolio(filter_type=None, filter_min_value=None, reference_date=None):
    """
    Orchestratore principale — coordina le funzioni di calcolo e filtro.
    - filter_type: filtra per categoria (opzionale)
    - filter_min_value: filtra per valore minimo in EUR (opzionale)
    - reference_date: data per calcolo delta in formato YYYY-MM-DD (opzionale)
    - restituisce un dizionario con posizioni e totali del portafoglio
    """
    # recupera e calcola i dati
    data = get_portfolio_data(reference_date)

    # calcola i totali e il weight % su tutto il portafoglio
    totals = calculate_totals(data)

    # applica i filtri dopo il calcolo dei totali
    filtered = apply_filters(data, filter_type, filter_min_value)

    return {
        "positions": filtered,
        **totals
    }


#aggiorna i prezzi in price_history oer tutti gli strumenti

def update_prices():
    """
    Recupera i prezzi aggiornati da yfinance per tutti gli strumenti
    in portafoglio e li salva in price_history.
    Viene chiamata ogni volta che l'utente lancia il comando 'update' dalla CLI.
    - restituisce un dizionario con i prezzi aggiornati per ogni ticker
    """
    positions = get_all_positions()

    if not positions:
        print("nessuna posizione in portafoglio")
        return {}

    # recupera tutti i prezzi in una sola chiamata
    tickers = [p["ticker"] for p in positions]
    current_prices = get_all_prices(tickers)

    updated = {}

    for position in positions:
        ticker = position["ticker"]
        position_id = position["id"]

        price = current_prices.get(ticker)

        if price is None:
            print(f"prezzo non disponibile per {ticker}, aggiornamento saltato")
            continue

        # salva il prezzo corrente in price_history
        add_price_snapshot(position_id, price)
        updated[ticker] = price
        print(f"{ticker} aggiornato : {price} €")

    return updated

