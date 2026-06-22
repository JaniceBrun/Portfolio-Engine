import sys
import os

# aggiunge la root del progetto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.market_api import get_current_price, get_all_prices, validate_ticker

def test():
    
    # test get_current_price su ticker valido
    print("Test get_current_price...")
    price = get_current_price("VWCE.MI")
    assert price is not None
    assert price > 0
    print(f"  ✓ VWCE.MI → {price} €")

    # test get_current_price su ticker non esistente
    price_invalid = get_current_price("PIPPO.MI")
    assert price_invalid is None
    print(f"  ✓ ticker non valido → None")

    # test get_all_prices su lista di ticker reali
    print("Test get_all_prices...")
    tickers = ["VWCE.MI", "GOLD.MI", "WBIT.DE", "XEON.MI"]
    prices = get_all_prices(tickers)
    assert len(prices) == 4
    for ticker, price in prices.items():
        print(f"  ✓ {ticker} → {price} €")

    # test validate_ticker
    print("Test validate_ticker...")
    assert validate_ticker("VWCE.MI") == True
    print(f"  ✓ VWCE.MI valido")
    assert validate_ticker("PIPPO.MI") == False
    print(f"  ✓ PIPPO.MI non valido")

    print("\nTutti i test passati ✓")

if __name__ == "__main__":
    test()