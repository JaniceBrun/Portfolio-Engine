"""Creazione classe Position"""

# classe position

class Position(object):
    """
    Rappresenta uno strumento finanziario in portafoglio
    Corrisponde ad un record nella tabella del db
    """
    #attributi di classe
    VALID_TYPES = ("etf", "etc", "etn", "azione", "obbligazione", "crypto")
    #mappa categorie macro
    MACRO_CATEGORIES = {
        "etf": "Investment",
        "etc": "Investment",
        "etn": "Investment",
        "azione": "Investment",
        "obbligazione": "Bonds & Money",
        "crypto": "Investment",
    }
    def __init__(self, id, ticker, name, type, currency="EUR", quantity=0, avg_price=0, total_cost=0, current_price=0, current_value=0, pl_abs=0, pl_pct=0, weight_pct=0):
        self.__id = id
        self.__ticker = ticker
        self.__name = name
        self.__currency = currency
        self.__type = type #usa setter x validaz
        self.__quantity = quantity
        self.__avg_price = avg_price
        self.__total_cost = total_cost
        self.__current_price = current_price
        self.__current_value = current_value
        self.__pl_abs = pl_abs
        self.__pl_pct = pl_pct
        self.__weight_pct = weight_pct        

    #getter id
    @property
    def id(self):
        return self.__id
    
    # getter getter ticker
    @property
    def ticker(self):
        return self.__ticker
    
    #setter controlla che sia str e non vuota e la porta a MAIUSC
    @ticker.setter
    def ticker(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Ticker deve essere una stringa non vuota")
        self.__ticker = value.upper()

    #setter e getter per name
    @property
    def name(self):
        return self.__name
    
    #setter controlla che name non sia vuota e sia str
    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("name deve essere una stringa non vuota")
        self.__name = value

    #getter e setter per currency
    @property
    def currency(self):
        return self.__currency
    
    #setter controlla currency sia str non vuota
    @currency.setter
    def currency(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("currency deve essere una stringa non vuota")
        self.__currency = value.upper()

    # getter e setter type
    @property
    def type(self):
        return self.__type
    
    @type.setter
    def type(self, value):
        if value not in self.VALID_TYPES:
            raise ValueError("categoria non presente")
        self.__type = value

    #getter quantity
    @property
    def quantity(self):
        return self.__quantity

    # getter avg_price
    @property
    def avg_price(self):
        return self.__avg_price
    
    # getter total_cost
    @property
    def total_cost(self):
        return self.__total_cost

    # getter current_price
    @property
    def current_price(self):
        return self.__current_price

    # getter current_value
    @property
    def current_value(self):
        return self.__current_value

    # pl_abs
    @property
    def pl_abs(self):
        return self.__pl_abs

    # pl_pct
    @property
    def pl_pct(self):
        return self.__pl_pct

    # weight_category      
    @property
    def weight_pct(self):
        return self.__weight_pct        

    @property
    def macro_category(self) -> str:
        """
        Restituisce la categoria macro dello strumento
        """
        return self.MACRO_CATEGORIES.get(self.type, "Altro")

    #METODI DELLA CLASSE
    @classmethod
    def from_dict(cls, data: dict) ->Position:
        """
        Metodo che crea oggetto position da un dict
        Converte i risultati delle query sql in oggetti
        """
        return cls(
            id = data["id"],
            ticker = data["ticker"],
            name = data["name"],
            type = data["type"],
            currency = data.get("currency", "EUR"),
            quantity = data.get("quantity", 0),
            avg_price = data.get("avg_price", 0),
            total_cost = data.get("total_cost", 0),
            current_price = data.get("current_price", 0),
            current_value = data.get("current_value", 0),
            pl_abs = data.get("pl_abs", 0),
            pl_pct = data.get("pl_pct", 0),
            weight_pct = data.get("weight_pct", 0),            
        )
    
    def to_dict(self) -> dict:
        """
        Converte oggetto Position un un dict
        utile per serializzare output
        """
        return {
            "id": self.id,
            "ticker": self.ticker,
            "name": self.name,
            "type": self.type,
            "currency": self.currency,
            "quantity": self.quantity,
            "avg_price": self.avg_price,
            "total_cost": self.total_cost,
            "current_price": self.current_price,
            "current_value": self.current_value,
            "pl_abs": self.pl_abs,
            "pl_pct": self.pl_pct,
            "weight_pct": self.weight_pct,            
        }
    
    # metodi rappresentazione
    def __repr__(self) -> str:
        return f"Position(ticker={self.ticker}, name={self.name}, type={self.type})"

    def __str__(self) -> str:
        return f"{self.ticker} - {self.name} ({self.type.upper()})"    





