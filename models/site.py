from __future__ import annotations

from decimal import Decimal

BASE_RATE = Decimal(7550)
AC_RATE = Decimal(150)
SEWER_RATE = Decimal(300)


class Site:

    def __init__(
        self,
        site_number: int,
        cabin: bool = True,
        ac: bool = True,
        sewer: bool = True,
    ):

        self.site_number = site_number
        self.cabin = cabin
        self.ac = ac
        self.sewer = sewer

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Site:
        return Site(
            int(row["Site Number"]),
            bool(int(row["Cabin"])),
            bool(int(row["AC"])),
            bool(int(row["Sewer"])),
        )

    def calc_annual_fees(self) -> Decimal:
        return BASE_RATE + int(self.ac) * AC_RATE + int(self.sewer) * SEWER_RATE

    def to_dict(self) -> dict[str, str]:
        return {
            "Site Number": str(self.site_number),
            "Cabin": str(int(self.cabin)),
            "AC": str(int(self.ac)),
            "Sewer": str(int(self.sewer)),
        }
