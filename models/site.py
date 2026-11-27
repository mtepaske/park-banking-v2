from __future__ import annotations

from decimal import Decimal

from services.settings import get_setting


class Site:
    """
    Tracks Site information

    Attributes
    ----------
    site_number : The number of the site
    cabin : Whether the site is a cabin or a van
    ac : Whether the site has an air conditioner
    sewer : Whether the site is sewered
    """

    def __init__(
        self,
        site_number: int,
        cabin: bool = True,
        ac: bool = True,
        sewer: bool = True,
    ) -> None:
        """
        Initialises the class

        Parameters
        ----------
        site_number : int
            The number of the site

        cabin : bool
            Whether the site is a cabin or a van. Defaults to True

        ac : bool
            Whether the site has an air conditioner. Defaults to True

        sewer : bool
            Whether the site is sewered. Defaults to True
        """

        self.site_number = site_number
        self.cabin = cabin
        self.ac = ac
        self.sewer = sewer

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Site:
        """
        Construct a Site from the row of a CSV file

        Parameters
        ----------
        row : dict[str, str]
            The row of the CSV file containing site information

        Returns
        -------
        Site
        """

        return Site(
            int(row["Site Number"]),
            bool(int(row["Cabin"])),
            bool(int(row["AC"])),
            bool(int(row["Sewer"])),
        )

    def calc_annual_fees(self) -> Decimal:
        """
        Calculate the annual fees of the site

        Returns
        -------
        Decimal
        """

        # Get the fees from settings
        base_rate = Decimal(get_setting("annual_fees_base_rate"))
        ac_rate = Decimal(get_setting("annual_fees_ac_rate"))
        sewer_rate = Decimal(get_setting("annual_fees_sewer_rate"))

        return base_rate + int(self.ac) * ac_rate + int(self.sewer) * sewer_rate

    def to_dict(self) -> dict[str, str]:
        """
        Generate a dictionary to represent this instance

        Returns
        -------
        dict[str, str]
        """

        return {
            "Site Number": str(self.site_number),
            "Cabin": str(int(self.cabin)),
            "AC": str(int(self.ac)),
            "Sewer": str(int(self.sewer)),
        }
