from appstate import AppState
from models.account import Account
from models.charge import Charge


class Matcher:
    """
    A helper class to facilitate matching charges to accounts

    Attributes
    ----------
    state : The current application state
    """

    def __init__(self, appstate: AppState) -> None:
        """
        Initialises the class

        Parameters
        ----------
        appstate : AppState
            The current application state
        """

        self.state = appstate

    def clean_desciption(self, charge: Charge) -> set[str]:
        """
        Filter out words to ignore from a charges details

        Parameters
        ----------
        charge : Charge
            The charge to filter the details of

        Returns
        -------
        set[str] : The filtered details
        """

        description = set()
        for word in charge.details.split():
            if word not in self.state.ignore:
                description.add(word)

        return description

    def keyword_match(self, charge: Charge) -> list[Account]:
        """
        Match charge details to accounts on the charge detials and account aliases

        Parameters
        ----------
        charge : Charge
            The charge to match

        Returns
        -------
        list[Account] : The possible matching accounts
        """

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
        """
        Add charges to the mactching account history

        Parameters
        ----------
        account : Account
            The account to add a charge to

        charge : Charge
            The charge to add in the account history

        particualrs : str
            A description of the charge type. Defaults to Direct Deposit
        """

        charge.particulars = particualrs
        account.history.add(charge)

    def match_all_single(self) -> bool:
        """
        Match charges to an account. Autonmatically assigns charges where only one possible match was found

        Returns
        -------
        bool : True if any single possiblilty matches were found. False otherwise
        """

        match_found = False

        for charge, account in self.state.charges.items():
            if account is None:
                possiblities = self.keyword_match(charge)

                if len(possiblities) == 1:
                    self.state.match_charge(charge, possiblities[0])
                    match_found = True

        return match_found
