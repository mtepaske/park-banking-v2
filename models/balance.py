from __future__ import annotations

from decimal import Decimal

from models.charge import Charge


class Balance:
    """
    Tracks the balance information fo a class

    Attributes
    ----------
    remaining : The remaining amount left from this current fincial years fees
    outstanding : The outstanding amount from previous fincial years fees
    credit : The credit on the account
    annual_fees : The annual fees of the account
    """

    def __init__(self, balance: Decimal, annual_fees: Decimal):
        """
        Initialises the class

        Parameters
        ----------
        balance : Decimal
            The total balance on the account. Positive values is for an amount owed, A negative amount is for a account in credit

        annual_fees : Decimal
            The annual fees of an account
        """

        self.remaining = Decimal(0)
        self.outstanding = Decimal(0)
        self.credit = Decimal(0)
        self.annual_fees = annual_fees

        if balance < 0:
            self.credit = abs(balance)
        elif balance <= self.annual_fees:
            self.remaining += balance
        elif balance > self.annual_fees:
            self.remaining = annual_fees
            self.outstanding = balance - annual_fees

    @property
    def total_balance(self) -> Decimal:
        """Gets the total balance of the account"""

        return self.remaining + self.outstanding - self.credit

    def add_payment(self, charge: Charge) -> None:
        """
        Add a payment

        Parameters
        ----------
        charge : Charge
            The payment to add
        """

        amount = charge.amount

        # Validation
        if amount <= 0:
            raise WrongChargeAmount(
                message="Payment Must Be Greater Then 0", charge=charge
            )

        if amount < self.outstanding:
            self.outstanding = -amount
            return
        else:
            amount = -self.outstanding
            self.outstanding = Decimal(0)

        if amount < self.remaining:
            self.remaining = -amount
            return
        else:
            amount = -self.remaining
            self.remaining = Decimal(0)

        self.credit += amount

    def add_fee(self, charge: Charge) -> None:
        """
        Add a fee

        Parameters
        ----------
        charge : Charge
           The fee to add
        """

        amount = charge.amount

        # Validation
        if amount >= 0:
            raise WrongChargeAmount(
                message="Payment Must Be Less Then 0", charge=charge
            )

        if self.credit > 0:
            if self.credit >= amount:
                self.credit = -charge.amount
                return
            else:
                amount = -self.credit
                self.credit = Decimal(0)

        self.remaining += amount

        if self.remaining > self.annual_fees:
            self.outstanding += self.remaining - self.annual_fees
            self.remaining = self.annual_fees


class WrongChargeAmount(Exception):
    """Raised when a charge has the wrong sign"""

    def __init__(self, message: str, charge: Charge):
        super().__init__(message)
        self.message = message
        self.charge = charge

    def __str__(self) -> str:
        return f"{self.message}\n{self.charge}"
