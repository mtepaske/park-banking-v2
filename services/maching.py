from models.account import Account
from models.charge import Charge


class Matcher:

    def __init__(self, accounts: set[Account], ignore: set[str]) -> None:
        self.accounts = accounts
        self.ignore = ignore
        self.unknown = set()

    def clean_desciption(self, charge: Charge) -> set[str]:
        description = set()

        for word in charge.details.split():
            if word not in self.ignore:
                description.add(word)

        return description

    def keyword_match(self, charge: Charge) -> list[Account]:
        description = self.clean_desciption(charge)

        possibilities = []

        for word in description:
            found = False
            for account in self.accounts:
                if word in account.aliases:
                    possibilities.append(account)
                    found = True
            if not found:
                self.unknown.add(word)

        return possibilities

    @staticmethod
    def assign_charge(
        account: Account, charge: Charge, particualrs: str = "Direct Deposit"
    ) -> None:
        charge.particulars = particualrs
        account.history.add(charge)
