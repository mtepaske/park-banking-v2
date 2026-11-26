from appstate import AppState
from models.account import Account
from models.charge import Charge


class Matcher:

    def __init__(self, appstate: AppState) -> None:
        self.state = appstate

    def clean_desciption(self, charge: Charge) -> set[str]:
        description = set()
        for word in charge.details.split():
            if word not in self.state.ignore:
                description.add(word)
        return description

    def keyword_match(self, charge: Charge) -> list[Account]:
        description = self.clean_desciption(charge)
        possibilities = []
        for word in description:
            found = False
            for account in self.state.accounts:
                if word in account.aliases:
                    possibilities.append(account)
                    found = True
            if not found:
                self.state.add_unknown(word)
        return possibilities

    @staticmethod
    def assign_charge(
        account: Account, charge: Charge, particualrs: str = "Direct Deposit"
    ) -> None:
        charge.particulars = particualrs
        account.history.add(charge)

    def match_all_single(self) -> bool:
        match_found = False
        for charge, account in self.state.charges.items():
            if account is None:
                possiblities = self.keyword_match(charge)
                if len(possiblities) == 1:
                    self.state.match_charge(charge, possiblities[0])
                    match_found = True

        return match_found
