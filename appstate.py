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
        self.charges: dict[Charge, Account | None] = {}
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

    # Accounts
    def add_account(self, account: Account):
        self.accounts.add(account)
        self.notify_changed()

    def remove_account(self, account: Account):
        self.accounts.remove(account)
        self.notify_changed()

    def clear_accounts(self):
        self.accounts.clear()
        self.notify_changed()

    def append_accounts(self, accounts: set[Account]):
        for account in accounts:
            self.accounts.add(account)
        self.notify_changed()

    def replace_accounts(self, accounts: set[Account]):
        self.accounts = accounts
        self.notify_changed()

    # Sites
    def add_site(self, site: Site):
        self.sites.add(site)
        self.notify_changed()

    def remove_site(self, site: Site):
        self.sites.remove(site)
        self.notify_changed()

    def clear_sites(self):
        self.sites.clear()
        self.notify_changed()

    def append_sites(self, sites: set[Site]):
        for site in sites:
            self.sites.add(site)
        self.notify_changed()

    def replace_sites(self, sites: set[Site]):
        self.sites = sites
        self.notify_changed()

    # Charges
    def add_charge(self, charge: Charge):
        self.charges[charge] = None
        self.notify_changed()

    def remove_charge(self, charge: Charge):
        self.charges.pop(charge)
        self.notify_changed()

    def clear_charges(self):
        self.charges.clear()
        self.notify_changed()

    def match_charge(self, charge: Charge, account: Account):
        self.charges[charge] = account
        self.notify_changed()

    def remove_match(self, charge: Charge):
        self.charges[charge] = None
        self.notify_changed()

    def append_charges(self, charges: set[Charge]):
        for charge in charges:
            self.charges[charge] = None
        self.notify_changed()

    def replace_charges(self, charges: set[Charge]):
        self.clear_charges()
        self.append_charges(charges)

    # Words to Ignore
    def add_ignore(self, word: str):
        self.ignore.add(word)
        self.notify_changed()

    def remove_ignore(self, word: str):
        self.ignore.remove(word)
        self.notify_changed()

    def clear_ignore(self):
        self.ignore.clear()
        self.notify_changed()

    # Unknown words
    def add_unknown(self, word: str):
        self.unknown.add(word)
        self.notify_changed()

    def remove_unknown(self, word: str):
        self.unknown.remove(word)
        self.notify_changed()

    def clear_unknown(self):
        self.unknown.clear()
        self.notify_changed()
