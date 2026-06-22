"""Creazione classe Purchase"""
#import 

from datetime import date

#creazione classe purchase, è il singolo acquisto che corrisponde a un record nel db

class Purchase(object):
    """
    Rappresenta un singolo acquisto di uno strumento.
    Corrisponde a un record nella tabella purchases del db.   
    """
    def __init__(self, id, position_id,  purchased_on, quantity, price):
        self.__id = id
        self.__position_id = position_id
        self.__purchased_on = purchased_on
        #per quantoty e price uso validazione diretta senza properties
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("quantity deve essere un numero positivo")
        self.__quantity = float(quantity)

        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price deve ssere un num positivo")
        self.__price = round(float(price), 4)

    #getter per id
    @property
    def id(self):
        return self.__id
    
    # getter per position_id
    @property
    def position_id(self):
        return self.__position_id
    
    # getter per quantity
    @property
    def quantity(self):
        return self.__quantity
    
    #getter per price
    @property
    def price(self):
        return self.__price
    
    # getter e setter per purchased_on con validazione formato data
    @property
    def purchased_on(self):
        return self.__purchased_on
    
    @purchased_on.setter
    def purchased_on(self, value):
        if isinstance(value, str):
            try:
                date.fromisoformat(value)
                self.__purchased_on = value
            except ValueError:
                raise ValueError("purchased_on deve essere in formato YYYY-MM-DD")
        else:
            raise ValueError("purchased_on deve essere una stringa")
        
    #SEZIONE METODI

    @classmethod
    def from_dict(cls, data):
        """
        Crea un oggetto Purchase da un dict
        """
        return cls(
            id = data["id"],
            position_id = data["position_id"],
            quantity = data["quantity"],
            price = data["price"],
            purchased_on = data["purchased_on"]
        )
        
    def to_dict(self):
        """
        Converte oggetto purchase in dict
        """
        return {
            "id": self.__id ,
            "position_id": self.__position_id ,
            "quantity": self.__quantity ,
            "price": self.__price ,
            "purchased_on": self.__purchased_on
        }

# metodo per il calcolo
    def total_cost(self):
        """
        Calcoma il costo tot dell'acquisto( quantita x prezzo)
        """
        return round(self.__quantity * self.__price, 2)

# metodi rappresentazione
    def __repr__(self):
        return f"Purchase(position_id={self.position_id}, qty={self.quantity}, price={self.price}, date={self.purchased_on})"

    def __str__(self):
        return f"Acquisto {self.quantity} quote a {self.price}€ il {self.purchased_on}"