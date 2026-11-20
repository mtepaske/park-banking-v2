from models.balance import Balance
from models.charge import Charge
from models.person import Person
from models.site import Site


class Account:

    def __init__(
        self,
        site: Site,
        balance: Balance,
        primary: Person,
        secondary: Person | None = None,
        active: bool = True,
        id: int | None = None,
    ):

        self.site = site
        self.balance = balance
        self.primary = primary
        self.secondary = secondary
        self.history = set()
        self.aliases = {}
        self.active = active
        self.id = id

    def find_aliases(self):
        self.alaises = {str(self.site.site_number): "Site Number"}

        for alias in self.primary.aliases:
            self.aliases[alias] = "Primary"

        if self.secondary is not None:
            for alias in self.secondary.aliases:
                self.alaises[alias] = "Secondary"

    def change_site_number(self, site_number: int):
        self.site.site_number = site_number
        self.find_aliases()

    def change_primary(self, person: Person):
        self.primary = person
        self.find_aliases()

    def change_secondary(self, person: Person):
        self.secondary = person
        self.find_aliases()

    def add_charge(self, charge: Charge):

        self.history.add(charge)

        if charge.amount > 0:
            self.balance.add_payment(charge)

        else:
            self.balance.add_fee(charge)
