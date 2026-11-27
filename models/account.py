from __future__ import annotations

from decimal import Decimal

from models.balance import Balance
from models.charge import Charge
from models.person import Person
from models.site import Site
from services.date import start_of_fy


class Account:
    """
    Tracks status of an account

    Attributes
    ----------
    site : The Site associated with the account
    primary : The Person who is the primary site holder
    secondary : The Person who is the secondary site holder
    aliases : The aliases used to match charges to
    active : The active status of the account
    id : The database id of the account
    history : The transaction history of the account
    balance : The Balance associated with the account
    """

    def __init__(
        self,
        site: Site,
        primary: Person,
        secondary: Person | None = None,
        history: set[Charge] | None = None,
        active: bool = True,
        id: int | None = None,
    ) -> None:
        """
        Initialises the class

        Parameters
        ----------
        site : Site
            The Site associated with the account

        primary : Person
            The primary site holder of the account

        secondary : Person | None
            The secondary site holder of the account. Defaults to None

        history : set[Charge] | None
            The fincanical history of the account. Defaults to None

        active : bool
            The active status of the account. Defaults to None

        id : int | None
            The database id of the account
        """

        self.site = site
        self.primary = primary
        self.secondary = secondary
        self.aliases = {}
        self.active = active
        self.id = id

        if history is None:
            history = set()
        self.history = history

        # Create the Balance class to track account balance
        balance = Decimal(0)
        for charge in self.history:
            balance += charge.amount
        self.balance = Balance(balance, self.site.calc_annual_fees())

    @property
    def total(self) -> Decimal:
        """Gets the total balance of the account"""

        return self.balance.total_balance

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Account:
        """
        Construct an Account from the row of a CSV file

        Parameters
        ----------
        row : dict[str, str]
            The row of the CSV file containing account information

        Returns
        -------
        Account
        """

        # Construct the Site
        site = Site(
            site_number=int(row["Site Number"]),
            cabin=bool(int(row["Cabin"])),
            ac=bool(int(row["AC"])),
            sewer=bool(int(row["Sewer"])),
        )

        # Construct the primary site holder
        primary = Person(
            name=row["Primary Site Holder"],
            aliases={alias for alias in row["Primary Aliases"].split(",")},
            phone_number=row["Primary Phone Number"],
            email=row["Primary Email"],
            id=int(row["Primary ID"]),
        )

        # Construct the secondary site holder
        if row["Secondary Site Holder"] != "":
            secondary = Person(
                name=row["Secondary Site Holder"],
                aliases={alias for alias in row["Secondary Aliases"].split(",")},
                phone_number=row["Secondary Phone Number"],
                email=row["Secondary Email"],
                id=int(row["Secondary ID"]),
            )
        else:
            secondary = None

        active = bool(int(row["Active"]))
        id = int(row["ID"])

        # Generate a default charge history
        history = {
            Charge(
                date=start_of_fy(),
                amount=Decimal(row["Total Balance"]) - Decimal(row["Annual Fees"]),
                details="Generated Charge",
                particulars="bf",
            ),
            Charge(
                date=start_of_fy(),
                amount=Decimal(row["Annual Fees"]),
                details="Generated Charge",
                particulars="af",
            ),
        }

        # Return the account
        return Account(
            site=site,
            primary=primary,
            secondary=secondary,
            history=history,
            active=active,
            id=id,
        )

    def find_aliases(self) -> None:
        """Collect the aliases of the site holders and the site number"""

        # Add the site number
        self.alaises = {str(self.site.site_number): "Site Number"}

        # Add the primary aliases
        for alias in self.primary.aliases:
            self.aliases[alias] = "Primary"

        # Add the secondary aliases
        if self.secondary is not None:
            for alias in self.secondary.aliases:
                self.alaises[alias] = "Secondary"

    def change_site(self, site: Site) -> None:
        """
        Change the Site associated with the Account

        Parameters
        ----------
        site : Site
            The new Site
        """

        self.site = site
        self.find_aliases()

    def change_primary(self, person: Person) -> None:
        """
        Change the primary site holder

        Parameters
        ----------
        person : Person
            The new primary site holder
        """

        self.primary = person
        self.find_aliases()

    def change_secondary(self, person: Person) -> None:
        """
        Change the secondary site holder

        Parameters
        ----------
        person : Person
            The new secondary site holder
        """

        self.secondary = person
        self.find_aliases()

    def add_charge(self, charge: Charge) -> None:
        """
        Add a charge to the history

        Parameters
        ----------
        charge : Charge
            The Charge to add
        """

        self.history.add(charge)

        if charge.amount > 0:
            self.balance.add_payment(charge)
        else:
            self.balance.add_fee(charge)

    def to_dict(self) -> dict[str, str]:
        """
        Generate a dictionary to represent this instance

        Returns
        -------
        dict[str, str]
        """

        return {
            "ID": str(self.id),
            "Site Number": str(self.site.site_number),
            "Primary Site Holder": self.primary.name,
            "Secondary Site Holder": (
                self.secondary.name if self.secondary is not None else "None"
            ),
            "Annual Fees": str(self.balance.annual_fees),
            "Remianing From This Fincial Year": str(self.balance.remaining),
            "Outstanding From Previous Fincial Years": str(self.balance.outstanding),
            "Credit": str(self.balance.credit),
            "Total Balance": str(self.balance.total_balance),
            "Active": str(int(self.active)),
            "Primary ID": str(self.primary.id),
            "Primary Aliases": ",".join(self.primary.aliases),
            "Primary Phone Number": self.primary.phone_number,
            "Primary Email": self.primary.email,
            "Secondary ID": (
                str(self.secondary.id) if self.secondary is not None else "None"
            ),
            "Secondary Aliases": (
                ",".join(self.secondary.aliases)
                if self.secondary is not None
                else "None"
            ),
            "Secondary Phone Number": (
                self.secondary.phone_number if self.secondary is not None else "None"
            ),
            "Secondary Email": (
                self.secondary.email if self.secondary is not None else "None"
            ),
            "Cabin": str(int(self.site.cabin)),
            "AC": str(int(self.site.ac)),
            "Sewer": str(int(self.site.sewer)),
        }
