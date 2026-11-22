from collections.abc import Callable

from models.account import Account
from models.charge import Charge
from services.database import Repository


class AppState:

    def __init__(self, repo: Repository) -> None:

        self.repo = repo
        self._listeners: list[Callable] = []

        self.accounts: list[Account] = []
        self.unmatched: list[Charge] = []
        self.matched: list[Charge] = []
        self.ignore: set[str] = set()
        self.unknown: set[str] = set()

    def subscribe(self, callback):
        self._listeners.append(callback)

    def unsubscribe(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def notify_changed(self):
        for callback in self._listeners.copy():
            callback()

    def add_account(self, account: Account):
        self.accounts.append(account)

    def remove_account(self, account: Account):
        self.accounts.remove(account)

    def clear_accounts(self):
        pass

    def add_unmatched(self, charge: Charge):
        self.unmatched.append(charge)

    def remove_unmactched(self, charge: Charge):
        self.unmatched.remove(charge)

    def clear_unmatched(self):
        pass

    def add_matched(self, charge: Charge):
        self.matched.append(charge)

    def remove_matched(self, charge: Charge):
        self.matched.remove(charge)

    def clear_matched(self):
        pass

    def matched_charge(self, charge: Charge):
        self.remove_unmactched(charge)
        self.add_matched(charge)

    def add_ignore(self, word: str):
        pass

    def remove_ignore(self, word: str):
        pass

    def clear_ignore(self):
        pass

    def add_unknown(self, word: str):
        pass

    def remove_unknown(self, word: str):
        pass

    def clear_unknown(self):
        pass
