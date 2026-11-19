class Site:

    def __init__(
        self,
        site_number: int,
        cabin: bool = True,
        ac: bool = True,
        sewer: bool = True,
        id: int | None = None,
    ):

        self.site_number = site_number
        self.cabin = cabin
        self.ac = ac
        self.sewer = sewer
        self.id = id
