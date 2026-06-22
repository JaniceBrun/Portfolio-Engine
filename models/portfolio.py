"""Creazione classe Portfolio"""
from typing import List
from models.position import Position

class Portfolio(object):
    """
    Rappreseta l'intero portafoglio dell'utente.
    Contiene una lista di posizioni e i loro acquisti
    """

    def __init__(self, positions=None, total_value=0.0, total_cost=0.0, pl_total_abs=0.0, pl_total_pct=0.0):
        """
        Inizializza il portafoglio.
        -positions: lista di posizioni( opzionale, default lista vuota)
        -total_value, total_cost, pl_total_abs, pl_total_pct: dati iniziali(opzionali)
        """
        self.__positions = positions if positions is not None else []
        self.__total_value = total_value
        self.__total_cost = total_cost
        self.__pl_total_abs = pl_total_abs
        self.__pl_total_pct = pl_total_pct

    # getter position
    @property
    def positions(self) -> List[Position]:
        """
        Restituisce lista posizione
        serve a report_engine per iterare posizioni
        """
        return self.__positions
    
    # getter  total_value
    @property
    def total_value(self):
        """
        Valore attuale del pf
        serve nel report_engine x il titolo
        """
        return self.__total_value
    
    #getter total_cost
    @property
    def total_cost(self):
        """
        Costo totale investito nel pf
        serve nel report_eng per calcolare P/L
        """
        return self.__total_cost
    
    # getter pl_total_abs
    @property
    def pl_total_abs(self):
        """
        P/L assoluto totale del pf in eu
        serve a report_engie
        """
        return self.__pl_total_abs
    
    # getter pl_total_pct
    @property
    def pl_total_pct(self):
        """
        P/L percentuale tot del pf
        serve a report_engine
        """
        return self.__pl_total_pct
    
    # METODI

    def add_position(self, position):
        """
        Aggiunge una posizione al pf
        """
        self.positions.append(position)

    def update_totals(self, total_value, total_cost, pl_total_abs, pl_total_pct):
        """
        Aggiorna i totali del pf
        Usato internamente dal report_engine dopo calcoli
        """
        self.__total_value = total_value
        self.__total_cost = total_cost
        self.__pl_total_abs = pl_total_abs
        self.__pl_total_pct = pl_total_pct

    def to_dict(self) -> dict:
        """
        Converte il pf in dict per serializzare
        """
        return{
            "positions": [pos.to_dict() for pos in self.positions ],
            "total_value": self.__total_value ,
            "total_cost": self.__total_cost ,
            "pl_total_abs": self.__pl_total_abs ,
            "pl_total_pct": self.__pl_total_pct ,
        }
    
    #METODI RAPPRESENTAZIONE
    def __repr__(self):
        return f"Portfolio(positions={len(self.positions)}, value={self.total_value}€, P/L={self.pl_total_pct}%)"

    def __str__(self):
        return f"Portafoglio con {len(self.positions)} strumenti | Valore: {self.total_value}€ | P/L: {self.pl_total_pct}%"    