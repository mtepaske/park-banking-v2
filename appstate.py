from collections.abc import Callable

from models.account import Account
from models.charge import Charge
from models.site import Site
from services.database import Repository


class AppState:

    def __init__(self, repo: Repository) -> None:

        self.repo = repo
        self._listeners: list[Callable] = []

        self.accounts: set[Account] = set()
        self.sites: set[Site] = set()
        self.unmatched: set[Charge] = set()
        self.matched: set[Charge] = set()
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
        self.accounts.add(account)
        self.notify_changed()

    def remove_account(self, account: Account):
        self.accounts.remove(account)
        self.notify_changed()

    def clear_accounts(self):
        self.accounts = set()
        self.notify_changed()

    def add_unmatched(self, charge: Charge):
        self.unmatched.add(charge)
        self.notify_changed()

    def remove_unmactched(self, charge: Charge):
        self.unmatched.remove(charge)
        self.notify_changed()

    def clear_unmatched(self):
        self.unmatched = set()
        self.notify_changed()

    def add_matched(self, charge: Charge):
        self.matched.add(charge)
        self.notify_changed()

    def remove_matched(self, charge: Charge):
        self.matched.remove(charge)
        self.notify_changed()

    def clear_matched(self):
        self.macthed = set()
        self.notify_changed()

    def matched_charge(self, charge: Charge):
        self.remove_unmactched(charge)
        self.add_matched(charge)
        self.notify_changed()

    def add_ignore(self, word: str):
        self.ignore.add(word)
        self.notify_changed()

    def remove_ignore(self, word: str):
        self.ignore.remove(word)
        self.notify_changed()

    def clear_ignore(self):
        self.ignore = set()
        self.notify_changed()

    def add_unknown(self, word: str):
        self.unknown.add(word)
        self.notify_changed()

    def remove_unknown(self, word: str):
        self.unknown.remove(word)
        self.notify_changed()

    def clear_unknown(self):
        self.unknown = set()
        self.notify_changed()
