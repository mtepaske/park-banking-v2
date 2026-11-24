from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from services.date import get_date_from_str

PARTICULARS = Literal["u", "m", "dd", "cc", "ca", "af", "di", "bp", "eg", "bf", "c"]
# - Unmatched
# - Matched
# - Direct Deposit
# - Credit Card
# - Cash
# - Annual Fees
# - Discount
# - Boart Parking
# - Extra Guests
# - Balance Brought Forward
# - Custom


class Charge:

    def __init__(
        self,
        date: date,
        amount: Decimal,
        details: str,
        particulars: PARTICULARS = "u",
        id: int | None = None,
    ):

        self.id = id
        self.date = date
        self.amount = amount
        self.details = details
        self.particulars = particulars

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Charge:
        return cls(
            date=get_date_from_str(row["Date"]),
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    @classmethod
    def from_history_csv(cls, row: dict[str, str]) -> Charge:

        return cls(
            date=get_date_from_str(row["Date"]),
            amount=Decimal(row["Amount"]),
            details=row["Details"],
            particulars=cls.generate_particulars(row["Detials"]),
        )

    @staticmethod
    def generate_particulars(description: str) -> PARTICULARS:
        details = description.split()
        scores: dict[PARTICULARS, int] = {
            "dd": 0,
            "cc": 0,
            "ca": 0,
            "af": 0,
            "di": 0,
            "bp": 0,
            "eg": 0,
            "bf": 0,
        }

        for word in details:
            match word:

                case "direct":
                    scores["dd"] += 1

                case "deposit":
                    scores["dd"] += 1

                case "credit":
                    scores["cc"] += 1

                case "card":
                    scores["cc"] += 1

                case "cash":
                    scores["ca"] += 1

                case "annual":
                    scores["af"] += 1

                case "fees":
                    scores["af"] += 1

                case "discount":
                    scores["di"] += 1

                case "boat":
                    scores["bp"] += 1

                case "parking":
                    scores["bp"] += 1

                case "extra":
                    scores["eg"] += 1

                case "guest":
                    scores["eg"] += 1

                case "brought":
                    scores["bf"] += 1

                case "forward":
                    scores["bf"] += 1

        particular: PARTICULARS = "c"
        max: int = 0
        for code, score in scores.items():
            if score > max:
                particular, max = code, score

        return particular
