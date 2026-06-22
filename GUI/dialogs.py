
#sezione import
import tkinter as  tk
from tkinter import ttk, messagebox

# creazione classe AddPositionDialog per il dialog di aggiunta

class AddPositionDialog(object):
    """Dialog per aggiungere una nuova posizione al pf"""

    def __init__(self, parent: tk.Widget):
        """
        Inizializza il dialog
        - parent: finestra padre
        """
        self.__parent = parent
        self.__dialog = None
        self.__result = None

        #attributi privati per i campi
        self.__ticker_var = tk.StringVar()
        self.__name_var = tk.StringVar()
        self.__type_var = tk.StringVar()
        self.__quantity_var = tk.StringVar()
        self.__price_var = tk.StringVar()

    #--result--read only
    @property
    def result(self) -> dict:
        """Restituisce i dati da inserire nel dialog"""
        return self.__result
    
    # metodi privati
    def __create_dialog(self):
        """Crea la finestra di dialogo"""
        self.__dialog = tk.Toplevel(self.__parent)
        self.__dialog.title("Aggiungi Posizione")
        self.__dialog.geometry("400x350")
        self.__dialog.resizable(False, False)

        # rendi modale
        self.__dialog.transient(self.__parent)
        self.__dialog.grab_set()

        # crea widget
        self.__dialog.transient(self.__parent)
        self.__create_widgets()

    def __create_widgets(self):
        """Crea i campi del form
           - ticker, nome tipo quantita, prezzo"""
        main_frame = ttk.Frame(self.__dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ticker
        ttk.Label(main_frame, text="Ticker: ").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.__name_var, width=30).grid(row=1, column=1, pady=5)

        # Name
        ttk.Label(main_frame, text="Nome: ").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.__name_var, width=30).grid(row=1, column=1, pady=5)

        # Type
        ttk.Label(main_frame, text="Tipo: ").grid(row=2, column=0, sticky=tk.W, pady=5)
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self._type_var,
            values=["etf", "etc", "etn", "azione", "obbligazione", "crypto"],
            state="readonly",
            width=27            
        )
        type_combo.grid(row=2, column=1, pady=5)

        # Quantity
        ttk.Label(main_frame, text="Quantità:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self._quantity_var, width=30).grid(row=3, column=1, pady=5)

        # Price
        ttk.Label(main_frame, text="Prezzo (€):").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self._price_var, width=30).grid(row=4, column=1, pady=5)

        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Aggiungi", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annulla", command=self._on_cancel).pack(side=tk.LEFT, padx=5)


    def __on_ok(self):
        """Valida e salva i dati"""             
        try:
            #validazione minima
            ticker = self.__ticker_var.get().strip()
            name = self.__name_var.get().strip()
            type_ = self.__type_var.get().strip()
            quantity = float(self.__quantity_var.get())
            price = float(self.__price_var.get())

            if not all([ticker, name, type_]):
                messagebox.showerror("Errore", "Tutti i campi sono obbligatori")
                return

            if quantity <= 0 or price <= 0:
                messagebox.showerror("Errore", "Quantità e prezzo devono essere positivi")
                return

            # salva il risultato
            self._result = {
                "ticker": ticker,
                "name": name,
                "type": type_,
                "quantity": quantity,
                "price": price
            }

            self.__dialog.destroy()

        except ValueError:
            messagebox.showerror("Errore", "Quantità e prezzo devono essere numeri")

    def _on_cancel(self):
        """Chiude il dialog senza salvare."""
        self.__result = None
        self.__dialog.destroy()

    # Metodo puvbblico
    def show(self) -> dict:
        """
        Mostra il dialog e restituisce i dati inseriti.
        - restituisce: dizionario con i dati oppure None se annullato
        """
        self.__create_dialog()
        self.__parent.wait_window(self.__dialog)
        return self._result            


        




