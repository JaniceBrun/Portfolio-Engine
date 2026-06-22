"""Interfaccia grafica tkinter"""

# sezione import

import tkinter as tk
from tkinter import ttk

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
        self.__root.geometry("1200x700")
        self.__root.resizable(True, True)

        self.__bg_colour = "#f0f0f0"
        self.__header_color = "#1f4788"
        self.__text_color = "white"

        # frame
        self.__top_frame = None
        self.__center_frame = None

        # configurazione stile
        self.__setup_styles()

        # crea frame principali
        self.__create_widgets()

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

        placeholder = tk.Label(
            self.__center_frame,
            text="Qui andrà il portafoglio",
            font=("Arial", 14),
            bg=self.bg_colour            
        )
        placeholder.pack(pady=20)

        # pulsanti
        self.__create_button_frame()

    def __create_button_frame(self):
        """Crea i pulsanti di controlla"""
        button_frame = tk.Frame(self.__root, bg=self.bg_colour)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Aggiungi Posizione", width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Rimuovi Posizione", width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Aggiorna Prezzi", width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Genera Report", width=20).pack(side=tk.LEFT, padx=5)        

def main():
    """Funzione principale - avvia l'app """
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()