from __future__ import annotations

from decimal import Decimal

from models.charge import Charge


class Balance:

    def __init__(self, balance: Decimal, annual_fees: Decimal):

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
    def balance(self) -> Decimal:
        return self.remaining + self.outstanding - self.credit

    def add_payment(self, charge: Charge) -> None:

        amount = charge.amount

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

        amount = charge.amount

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

    def __init__(self, message: str, charge: Charge):
        super().__init__(message)
        self.message = message
        self.charge = charge

    def __str__(self) -> str:
        return f"{self.message}\n{self.charge}"
