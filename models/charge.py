from datetime import date
from decimal import Decimal


class Charge:

    def __init__(
        self, date: date, amount: Decimal, details: str, particulars: str = "u"
    ):

        self.date = date
        self.amount = amount
        self.details = details
        self.particulars = particulars
