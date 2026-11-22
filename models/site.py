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

    def calc_annual_fees(self) -> Decimal:
        return BASE_RATE + int(self.ac) * AC_RATE + int(self.sewer) * SEWER_RATE
