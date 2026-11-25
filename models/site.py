from __future__ import annotations

from decimal import Decimal

from services.settings import get_setting


class Site:

    def __init__(
        self,
        site_number: int,
        cabin: bool = True,
        ac: bool = True,
        sewer: bool = True,
    ) -> None:

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
        base_rate = Decimal(get_setting("annual_fees_base_rate"))
        ac_rate = Decimal(get_setting("annual_fees_ac_rate"))
        sewer_rate = Decimal(get_setting("annual_fees_sewer_rate"))
        return base_rate + int(self.ac) * ac_rate + int(self.sewer) * sewer_rate

    def to_dict(self) -> dict[str, str]:
        return {
            "Site Number": str(self.site_number),
            "Cabin": str(int(self.cabin)),
            "AC": str(int(self.ac)),
            "Sewer": str(int(self.sewer)),
        }
