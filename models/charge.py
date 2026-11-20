from datetime import date
from decimal import Decimal
from typing import Literal

PARTICULARS = Literal["u", "m", "dd", "cc", "ca", "af", "bp", "eg", "c"]
# - Unmatched
# - Matched
# - Direct Deposit
# - Credit Card
# - Cash
# - Annual Fees
# - Boart Parking
# - Extra Guests
# - Custom


class Charge:

    def __init__(
        self, date: date, amount: Decimal, details: str, particulars: PARTICULARS = "u"
    ):

        self.date = date
        self.amount = amount
        self.details = details
        self.particulars = particulars
