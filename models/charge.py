from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from services.date import get_date_from_str, get_str_from_date

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
        details: str = "",
        particulars: str = "Unmatched",
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
            particulars=row["Description"],
        )

    def to_history_dict(self) -> dict[str, str]:
        if self.amount > 0:
            debit = ""
            credit = str(abs(self.amount))
        else:
            debit = str(self.amount)
            credit = ""

        return {
            "Date": get_str_from_date(self.date),
            "Description": self.particulars,
            "Debit": debit,
            "Credit": credit,
        }
