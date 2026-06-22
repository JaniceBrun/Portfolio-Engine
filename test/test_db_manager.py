import sys
import os

# aggiungo la root del path del progetto coy python trova i moduli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from portfolio_engine.db.db_manager import (
    init_db, add_position, add_purchase, get_position_by_ticker,
    get_all_positions, get_position_summary, remove_position,
    update_purchase, add_price_snapshot, get_latest_price
)

def test():
    """inizializza db e crea tabelle"""
    init_db()
    print("DB inizializzato")

    #inserimento VWCE e primo acquisto
    pos_id = add_position("VWCE.MI", "Vanguard FTSE All-World", "etf")
    add_purchase(pos_id, 18, 139.37, "2025-02-21")
    add_purchase(pos_id, 18, 139.49, "2025-02-21")
    print("posizione e acquisti inseriti")

    #verifico che la posizione esista
    pos = get_position_by_ticker("VWCE.MI")
    assert pos is not None
    assert pos["ticker"] == "VWCE.MI"
    print("get_position_ny_ticker ok")

    # verifico calcolo prezzo medio
    summary = get_position_summary(pos_id)
    assert summary["total_quantity"] == 36
    print(F"get_position_summary OK → avg_price: {summary['avg_price']:.2f} €")

    #verifica get_all_position
    all_pos = get_all_positions()
    assert len(all_pos) == 1
    print("get_all_position ok")

    #aggiungo altro acquisto
    update_purchase(pos_id, 20, 127.99, "2025-03-17")
    summary = get_position_summary(pos_id)
    assert summary["total_quantity"] == 56
    print("update_purcase ok")

    # save e retry di un prezzo di mercato
    add_price_snapshot(pos_id, 161.61)
    latest = get_latest_price(pos_id)
    assert latest["price"] == 161.61
    print("add_price_snapshot ok")

    #rimuove posizione
    result = remove_position("VWCE.MI")
    assert result == True
    assert get_position_by_ticker("VWCE.MI") is None
    print("\nTutti i test passati")

if __name__ == "__main__":
    test()