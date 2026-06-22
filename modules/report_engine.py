"""REPORT ENGINE"""

# sezione import

from tabulate import tabulate #libreria formattazione tabelle ASCII
from models.position import Position #classe
from models.portfolio import Portfolio #classe

# sezione import per pdf
from reportlab.lib.pagesizes import letter ,A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
import os

# Funzione per creazione oggetto Position dai dati

def build_position_object(position_data: dict):
    """
    crea un oggetto Position da un dict di dati calcolati
    - position_data: dizionario con i dati di una posizione da portfolio_logic
    - restituisce un oggetto Position    
    """
    position = Position(
        id = position_data["id"],
        ticker = position_data["ticker"],
        name = position_data["name"],
        type = position_data["type"],
        currency = position_data.get("currency", "EUR"),
        quantity = position_data.get("quantity", 0),
        avg_price = position_data.get("avg_price", 0),
        total_cost = position_data.get("total_cost", 0),
        current_price = position_data.get("current_price", 0),
        current_value = position_data.get("current_value", 0),
        pl_abs = position_data.get("pl_abs", 0),
        pl_pct = position_data.get("pl_pct", 0),
        weight_pct = position_data.get("weight_pct", 0)        
    )
    return position

# Funzione per creare oggetto Portfolio dai dati calcolati

def build_portfolio_object(portfolio_data: dict) ->Portfolio:
    """
    Crea un oggetto Portfolio dai dati calcolati da portfolio_logic
    - portfolio_data: dizionario restituito da calculate_portfolio()
    - restituisce un oggetto Portfolio con tutte le posizioni e i totali    
    """
    # crea il Portfolio con i totali
    portfolio = Portfolio(
        total_value = portfolio_data["total_value"],
        total_cost = portfolio_data["total_cost"],
        pl_total_abs = portfolio_data["pl_total_abs"],
        pl_total_pct = portfolio_data["pl_total_pct"]
    )

    # converte e aggiunge ogni posizione
    for position_data in portfolio_data["positions"]:
        position = build_position_object(position_data)
        portfolio.add_position(position)

    return portfolio

# Funzione per stampare la tabella

def print_portfolio_table(portfolio: Portfolio):
    """
    Stampa una tabella formattata con tutte le posizioni del portafoglio.
    - portfolio: oggetto Portfolio con le posizioni    
    """
    headers = [
        "Ticker",
        "Nome",
        "Tipo",
        "Quantità",
        "Prezzo Medio",
        "Costo Totale",
        "Prezzo Corrente",
        "Valore Attuale",
        "P/L €",
        "P/L %",
        "Weight %"
    ]

    #costruzione dati per ogni riga
    rows = []
    for position in portfolio.positions:
        position: Position
        rows.append([
            position.ticker,
            position.name,
            position.type.upper(),
            f"{position.quantity:.0f}",
            f"€ {position.avg_price:.2f}",
            f"€ {position.total_cost:.2f}",
            f"€ {position.current_price:.2f}",
            f"€ {position.current_value:.2f}",
            f"€ {position.pl_abs:.2f}",
            f"{position.pl_pct:.2f}%",
            f"{position.weight_pct:.2f}%"            
        ])

    # stampa tabella
    print("\n" + "="*140)
    print(f"PORTAFOGLIO - Valore totale: € {portfolio.total_value:.2f}")
    print("="*140 + "\n")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print("\n" + "="*140)
    print(f"TOTALI | Costo: € {portfolio.total_cost:.2f} | Valore: € {portfolio.total_value:.2f} | P/L: € {portfolio.pl_total_abs:.2f} ({portfolio.pl_total_pct:.2f}%)")
    print("="*140 + "\n")    

    #funzione principale orchestratrice

def generate_report(portfolio_data: dict) -> None:
    """
    Genera un report completo del portafoglio
    Orchestratore principale del report_engine.
    - portafolio_data: dict restituito da portfolio_logic.calculare_portfolio()
    """
    #converte i dati in oggetti OOP
    portfolio = build_portfolio_object(portfolio_data)

    #stampa report
    print_portfolio_table(portfolio)

# Funzione per generare il pdf
def generate_pdf_report(portfolio: Portfolio, filename: str = None) -> None:
    """
    Genera un report in formato PDF del portafoglio.
    - portfolio: oggetto Portfolio con le posizioni
    - filename: percorso del file PDF (default: reports/portfolio_YYYY-MM-DD.pdf)    
    """
    if filename is None:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"reports/portfolio_{today}.pdf"

    # creazione docu pdf
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # crea dir report se non esiste
    os.makedirs("reports", exist_ok=True)

    #titolo
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1 # centrato
    )
    title = Paragraph("PORTFOLIO REPORT", title_style)
    story.append(title)

    # data generazione
    date_text = Paragraph(
        f"<font size=10>Generato il {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</font>",
        styles['Normal']
    )
    story.append(date_text)
    story.append(Spacer(1, 0.2 * inch))

    #tabella posizioni
    data = [["Ticker", "Nome", "Tipo", "Qty", "Prezzo Medio", "Costo Totale", "Prezzo Attuale", "Valore", "P/L €", "P/L %", "Weight %"]]
    
    for position in portfolio.positions:
        data.append([
            position.ticker,
            position.name[:20],  # tronca il nome
            position.type.upper(),
            f"{position.quantity:.0f}",
            f"€ {position.avg_price:.2f}",
            f"€ {position.total_cost:.2f}",
            f"€ {position.current_price:.2f}",
            f"€ {position.current_value:.2f}",
            f"€ {position.pl_abs:.2f}",
            f"{position.pl_pct:.2f}%",
            f"{position.weight_pct:.2f}%",
        ])

    # aggiunta totali
    data.append([
        "TOTALI", "", "", "",
        "", f"€ {portfolio.total_cost:.2f}",
        "", f"€ {portfolio.total_value:.2f}",
        f"€ {portfolio.pl_total_abs:.2f}",
        f"{portfolio.pl_total_pct:.2f}%",
        "100.00%"
    ])

    # creazione tabella
    table = Table(data, colWidths=[1*inch, 1.5*inch, 0.8*inch, 0.6*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch, 0.7*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8e8e8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))
    
    # summary
    summary_text = Paragraph(
        f"<b>Valore Totale:</b> € {portfolio.total_value:.2f} | "
        f"<b>Costo Totale:</b> € {portfolio.total_cost:.2f} | "
        f"<b>P/L Totale:</b> € {portfolio.pl_total_abs:.2f} ({portfolio.pl_total_pct:.2f}%)",
        styles['Normal']
    )
    story.append(summary_text)
    
    # genera il PDF
    doc.build(story)
    print(f"PDF generato: {filename}")
      
    