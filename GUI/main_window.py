"""Interfaccia grafica tkinter"""

# sezione import

import tkinter as tk
from tkinter import ttk, messagebox
from GUI.dialogs import AddPositionDialog
from db.db_manager import init_db, add_position, add_purchase, get_all_positions, remove_position, add_or_update_position
from modules.portfolio_logic import calculate_portfolio, update_prices

# Creazione Classe PortfolioApp:

class PortfolioApp(object):
    """"
    Applicazione GUI principale per Portfolio-Engine.
    Gestisce interfaccia grafica del portafoglio
    """
    def __init__(self, root: tk.Tk):
        """
        Inizializza l'applicazione
        - root: finestra principale dei tkinter
        """
        self.__root = root
        self.__root.title("Portfolio Engine")
        self.__root.geometry("1400x700")
        self.__root.resizable(True, True)

        # attributi di stato
        self.__bg_colour = "#f0f0f0"
        self.__header_color = "#1f4788"
        self.__text_color = "white"

        # frame - widget principali
        self.__top_frame = None
        self.__center_frame = None
        self.__treeview = None

        # inizializzazione db
        init_db()

        # configurazione stile
        self.__setup_styles()

        # crea frame principali
        self.__create_widgets()

        # refresh del pf
        self.__refresh_portfolio()

    #getter e setter per attributi privati
    
    #--root--read only
    @property
    def root(self) -> tk.Tk:
        """Restituisce la finestra principale"""
        return self.__root
    
    #--bg_colour--read write con validazione
    @property
    def bg_colour(self) -> str:
        """Restituisce il colore di sfondo"""
        return self.__bg_colour

    @bg_colour.setter
    def bg_colour(self, value: str):
        """Imposta il colore di sfondo"""
        if not isinstance(value, str):
            raise ValueError("bg_colour deve essere una stringa")
        self.__bg_colour

    #--header_colour--read write con validazione
    @property
    def header_color(self) -> str:
        """Restituisce il colore dell'header"""
        return self.__header_color
    
    @header_color.setter
    def header_color(self, value: str):
        """Imposta colore dell'header"""
        if not isinstance(value, str):
            raise ValueError("header_color deve essere una stringa")
        self.__header_color = value

    # --text-color--read write con validazione
    @property
    def text_color(self) -> str:
        """Restituisce il colore del testo"""
        return self.__text_color
    
    @text_color.setter
    def text_color(self, value: str):
        """Imposta il colore del testo"""
        if not isinstance(value, str):
            raise ValueError("Text_color delve essere una strina")

    #--top_frame--read only
    @property
    def top_frame(self):
        """Restituisce il frame superiore"""
        return self.__top_frame

    #--center_frame--read only
    @property
    def center_frame(self):
        """Restituisce il frame superiore"""
        return self.__center_frame
    
    # metodi classe -privati -> interni per implementazione

    def __setup_styles(self):
        """Configura i colori e gli altri stili"""
        self.__root.configure(bg=self.bg_colour)

    def __create_widgets(self):
        """Crea i widget principali"""
        # frame superiore - titolo
        self.__top_frame = tk.Frame(self.__root, bg=self.header_color, height=60)
        self.__top_frame.pack(fill=tk.X, padx=0, pady=0)

        title_label = tk.Label(
            self.__top_frame,
            text="Portfolio Engine",
            font=("Arial", 20, "bold"),
            fg=self.text_color,
            bg=self.header_color            
        )
        title_label.pack(pady=10)

        #frame centrale
        self.__center_frame = tk.Frame(self.__root, bg=self.bg_colour)
        self.__center_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        self.__create_treeview()

        #pulsanti
        self.__create_button_frame()

    def __create_treeview(self):
        """Crea tabella treeview per il pf"""
        tree_frame = ttk.Frame(self.__center_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # scrollbar verticale
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #colonne
        columns = ("Ticker", "Nome", "Tipo", "Quantità", "Prezzo Medio", "Costo Totale", 
                   "Prezzo Attuale", "Valore", "P/L €", "P/L %", "Weight %")
        
        # creazione Treeview
        self.__treeview = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        scrollbar.config(command=self.__treeview.yview)

        # definizione intestazione e lunghezza colonne
        widths = [80, 180, 60, 70, 90, 100, 100, 90, 90, 70, 80]
        for col, width in zip(columns, widths):
            self.__treeview.heading(col, text=col)
            self.__treeview.column(col, width=width, anchor=tk.CENTER)

        self.__treeview.pack(fill=tk.BOTH, expand=True)

        # placeholder = tk.Label(
        #     self.__center_frame,
        #     text="Qui andrà il portafoglio",
        #     font=("Arial", 14),
        #     bg=self.bg_colour            
        # )
        # placeholder.pack(pady=20)

        # # pulsanti
        # self.__create_button_frame()

    def __create_button_frame(self):
        """Crea i pulsanti di controlla"""
        button_frame = tk.Frame(self.__root, bg=self.bg_colour)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            button_frame,
            text="Aggiungi Posizione",
            width=20,
            command=self.__on_add_position
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Rimuovi Posizione",
            width=20,
            command=self.__on_remove_position
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Aggiorna Prezzi",
            width=20,
            command=self.__on_update_prices
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Genera Report",
            width=20,
            command=self.__on_generate_report
        ).pack(side=tk.LEFT, padx=5)


    def __refresh_portfolio(self):
        """Ricarica il pf dal db e aggiorna la Treeview"""
        try:
            # svuota la tabella
            for item in self.__treeview.get_children():
                self.__treeview.delete(item)

            # recupera i dati
            portfolio_data = calculate_portfolio()

            #aggiunge le righe
            for position in portfolio_data["positions"]:
                position: dict
                type_str: str = position["type"]

                self.__treeview.insert("", tk.END, values=(
                    position["ticker"],
                    position["name"], 
                    type_str.upper(),
                    f"{position['quantity']:.0f}",
                    f"€ {position['avg_price']:.2f}",
                    f"€ {position['total_cost']:.2f}",
                    f"€ {position['current_price']:.2f}",
                    f"€ {position['current_value']:.2f}",
                    f"€ {position['pl_abs']:.2f}",
                    f"{position['pl_pct']:.2f}%",
                    f"{position['weight_pct']:.2f}%",
                ))                 
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento del portafoglio: {e}")

    
    def __on_add_position(self):
        """Gestisce l'aggiunta di una nuona posizione"""
        dialog = AddPositionDialog(self.__root)
        result = dialog.show()

        if result:
            try:
                position_id = add_or_update_position(
                    result["ticker"],
                    result["name"],
                    result["type"],
                    result["quantity"],
                    result["price"]
                )
                messagebox.showinfo("Successo", f"Posizione {result['ticker']} aggiunta!")
                self.__refresh_portfolio()
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'aggiunta: {e}")

            # try:
            #     position_id = add_position(result["ticker"], result["name"], result["type"])
            #     add_purchase(position_id, result["quantity"], result["price"])
    def __on_remove_position(self):
        """Gestisce la rimozione di una posizione"""
        selected = self.__treeview.selection()
        if not selected:
            messagebox.showwarning("Attenzione", "Seleziona una posizione da rimuovere")
            return
        
        item = selected[0]
        ticker = self.__treeview.item(item)["values"][0]

        if messagebox.askyesno("Conferma", f"Rimuovere {ticker}?"):
            try:
                remove_position(ticker)
                messagebox.showinfo("Successo", f"Posizione {ticker} rimossa!")
                self.__refresh_portfolio()
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nella rimozione di {e}")

    def __on_update_prices(self): 
        """Gestisce la'ggiornamento dei prezzi"""
        try:
            updated = update_prices()
            messagebox.showinfo("Successo", f"prezzi aggiornati per {len(updated)} strumenti")
            self.__refresh_portfolio()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiornamento: {e}")

    def __on_generate_report(self):
        """Gestisce la generazione del report"""        
        messagebox.showinfo("Info", "Feature in sviluppo")
        # todo -> implement gen report


def main():
    """Funzione principale - avvia l'app """
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()