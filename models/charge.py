from __future__ import annotations

from datetime import date
from decimal import Decimal

from services.date import get_date_from_str, get_str_from_date


class Charge:
    """
    Represent a fincial transaction

    Attributes
    ----------
    id : The database id of the charge
    date : The date of the charge
    amount : The amount of the charge
    details : The details of the charge from the bank statement
    particulars : A description of the charge
    """

    def __init__(
        self,
        date: date,
        amount: Decimal,
        details: str = "",
        particulars: str = "Unmatched",
        id: int | None = None,
    ) -> None:
        """
        Initialises the class

        Parameters
        ----------
        date : date
            The date of the charge

        amount : Decimal
            The amount of the charge. Positive values indicate payments. Negative values indicate fees

        details : str
            The details of the charge from the bank statment

        particulars : str
            A description of the charge. Defaults to 'Unmatched'

        id : int | None
            The database id of the charge
        """

        self.id = id
        self.date = date
        self.amount = amount
        self.details = details
        self.particulars = particulars

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Charge:
        """
        Construct a Charge from the row of a CSV file

        Parameters
        ----------
        row : dict[str, str]
            The row of the CSV file containing charge information

        Returns
        -------
        Charge
        """

        return cls(
            date=get_date_from_str(row["Date"]),
            amount=Decimal(row["Amount"]),
            details=row["Transaction Details"],
        )

    @classmethod
    def from_history_csv(cls, row: dict[str, str]) -> Charge:
        """
        Construct a charge from the row of a CSV file

        Parameters
        ----------
        row : dict[str, str]
            The row of the CSV file containing charge information

        Returns
        -------
        Charge
        """

        return cls(
            date=get_date_from_str(row["Date"]),
            amount=Decimal(row["Amount"]),
            particulars=row["Description"],
        )

    def to_history_dict(self) -> dict[str, str]:
        """
        Generate a dictionary to represent this instance

        Returns
        -------
        dict[str, str]
        """

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
