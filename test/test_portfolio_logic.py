import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db_manager import init_db, add_position, add_purchase
from modules.portfolio_logic import (
    calculate_portfolio,
    update_prices,
    get_portfolio_data,
    calculate_totals,
    apply_filters
)

def setup():
    """Inizializza il db e inserisce dati reali per il test."""
    init_db()

    # inserisce i 4 strumenti reali
    id_vwce = add_position("VWCE.MI", "Vanguard FTSE All-World", "etf")
    id_gold = add_position("GOLD.MI", "Amundi Physical Gold",    "etc")
    id_wbit = add_position("WBIT.DE", "WisdomTree Physical Bitcoin", "etn")
    id_xeon = add_position("XEON.MI", "Xtrackers EUR Overnight Rate", "etf")

    # acquisti reali da Excel
    add_purchase(id_vwce, 18,  139.37, "2025-02-21")
    add_purchase(id_vwce, 18,  139.49, "2025-02-21")
    add_purchase(id_vwce, 20,  127.99, "2025-03-17")
    add_purchase(id_vwce, 22,  118.24, "2025-04-10")
    add_purchase(id_vwce, 25,  131.29, "2025-07-14")

    add_purchase(id_gold, 14,  112.80, "2025-07-10")
    add_purchase(id_gold,  7,  115.73, "2025-08-27")
    add_purchase(id_gold,  9,  122.09, "2025-09-08")

    add_purchase(id_wbit, 71,   22.73, "2025-09-08")

    add_purchase(id_xeon, 32,  148.10, "2026-01-06")

    print("✓ Dati inseriti")


def test():
    setup()

    # test update_prices — richiede connessione internet
    print("\nTest update_prices...")
    updated = update_prices()
    assert len(updated) > 0
    print(f"  ✓ prezzi aggiornati per {len(updated)} strumenti")

    # test get_portfolio_data
    print("\nTest get_portfolio_data...")
    data = get_portfolio_data()
    assert len(data) > 0
    for d in data:
        print(f"  ✓ {d['ticker']} → valore attuale: {d['current_value']} €")

    # test calculate_totals
    print("\nTest calculate_totals...")
    totals = calculate_totals(data)
    assert totals["total_value"] > 0
    assert totals["total_cost"]  > 0
    print(f"  ✓ valore totale PF:  {totals['total_value']} €")
    print(f"  ✓ costo totale PF:   {totals['total_cost']} €")
    print(f"  ✓ P/L totale:        {totals['pl_total_abs']} €")
    print(f"  ✓ rendimento totale: {totals['pl_total_pct']} %")

    # test apply_filters — filtra solo ETF
    print("\nTest apply_filters per tipo 'etf'...")
    etf_only = apply_filters(data, filter_type="etf")
    assert all(r["type"] == "etf" for r in etf_only)
    print(f"  ✓ trovati {len(etf_only)} ETF")

    # test calculate_portfolio completo
    print("\nTest calculate_portfolio...")
    portfolio = calculate_portfolio()
    assert "positions" in portfolio
    assert "total_value" in portfolio
    print(f"  ✓ portafoglio completo → {len(portfolio['positions'])} posizioni")

    # test filtro per valore minimo
    print("\nTest filtro valore minimo 5000 €...")
    portfolio_filtered = calculate_portfolio(filter_min_value=5000)
    for p in portfolio_filtered["positions"]:
        assert p["current_value"] >= 5000
        print(f"  ✓ {p['ticker']} → {p['current_value']} €")

    print("\nTutti i test passati ✓")


if __name__ == "__main__":
    test()