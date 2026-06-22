"""PORTFOLIO ENGINE - CLI principale"""

import argparse 
from db.db_manager import (
    init_db, add_position, add_purchase, get_all_positions, remove_position
)
from modules.portfolio_logic import calculate_portfolio , update_prices
from modules.report_engine import generate_report, build_portfolio_object, print_portfolio_table

def main():
    """
    Entry point app
    Gestisce i comandi da riga di comando
    """
    parser = argparse.ArgumentParser(
        description="Portfolio Engine - Gestisci il tuo portafoglio finanziario",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi di utilizzo:
  python main.py add --ticker VWCE.MI --name "Vanguard" --type etf --quantity 10 --price 150.50
  python main.py show
  python main.py show --type etf
  python main.py report
"""
    )

    subparser = parser.add_subparsers(dest="command", help="Comando da eseguire")

    # Comando add
    add_parser = subparser.add_parser("add", help="Aggiungi una nuova posizione")
    add_parser.add_argument("--ticker", required=True, help="Ticker dello strumento (es. VWCE.MI)")
    add_parser.add_argument("--name", required=True, help="Nome dello strumento")
    add_parser.add_argument("--type", required=True, choices=["etf", "etc", "etn", "azione", "obbligazione", "crypto"], help="Tipo dello strumento")
    add_parser.add_argument("--quantity", type=float, required=True, help="Quantità")
    add_parser.add_argument("--price", type=float, required=True, help="Prezzo di acquisto")

    # Comando remove
    remove_parser = subparser.add_parser("remove", help="Rimuovi una posizione")
    remove_parser.add_argument("--ticker", required=True, help="Ticker da rimuovere")

    # Comando show
    show_parser = subparser.add_parser("show", help="Mostra il portafoglio")
    show_parser.add_argument("--type", help="Filtra per tipo(etf, etc, etn, azione, obbligazione, crypto)")
    show_parser.add_argument("--min-value", type=float, help="Filtra per valore minimo in EUR")

    # Comando update
    update_parser = subparser.add_parser("update", help="Aggiorna i prezzi da yfinance")
    
    # Comando report
    report_parser = subparser.add_parser("report", help="Genera un report")
    report_parser.add_argument("--pdf", action="store_true", help="Genera report in PDF")
    report_parser.add_argument("--from", type=str, dest="from_date", help="Data inizio per delta (YYYY-MM-DD)")

    args = parser.parse_args()

    #inizializzo il db se non esiste

    init_db()


    # Gestione comandi 
    if args.command == "add":
        handle_add(args)
    elif args.command == "remove":
        handle_remove(args)
    elif args.command == "show":
        handle_show(args)
    elif args.command == "update":
        handle_update()
    elif args.command == "report":
        handle_report(args)
    else:
        parser.print_help()


def handle_add(args: argparse.Namespace):
    """
    Gestisce comando add
    """
    try:
        position_id = add_position(args.ticker, args.name, args.type)
        add_purchase(position_id, args.quantity, args.price)
        print(f"Posizione aggiunta: {args.ticker}")
    except Exception as e:
        print(f"Errore: {e}")

def handle_remove(args : argparse.Namespace):
    """
    Gestisce il comando remove
    """
    try:
        remove_position(args.ticker)
        print(f"Posizione rimossa: {args.ticker}")
    except Exception as e:
        print(f"Errore: {e}")


def handle_show(args: argparse.Namespace):
    """
    Gestisce il comando show
    """
    try:
        portfolio_data = calculate_portfolio(
            filter_type=args.type,
            filter_min_value=args.min_value
        )
        #debug
        # print(f"DEBUG: portfolio_data = {portfolio_data}")
        # print(f"DEBUG: keys = {portfolio_data.keys()}")
        
        generate_report(portfolio_data)
    except Exception as e:
        # import traceback
        print(f"Errore: {e}")
        # traceback.print_exc()


def handle_update():
    """
    Gestisce il comando update
    """
    try:
        updated = update_prices()
        print(f"Prezzi aggiornati per {len(updated)} strumenti")
    except Exception as e:
        print(f"Errore: {e}")


def handle_report(args: argparse.Namespace):
    """
    Gestisce il comando report
    """
    try:
        portfolio_data = calculate_portfolio(reference_date=args.from_date)
        
        # converte in oggetto Portfolio
        portfolio = build_portfolio_object(portfolio_data)
        
        if args.pdf:
            # genera PDF
            from modules.report_engine import generate_pdf_report
            generate_pdf_report(portfolio)
        else:
            # stampa report nel terminale
            print_portfolio_table(portfolio)
    except Exception as e:
        print(f"  ✗ Errore: {e}")


if __name__ == "__main__":
    main()