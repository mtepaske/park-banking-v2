class Person:

    def __init__(
        self,
        name: str,
        aliases: set[str] | None = None,
        phone_number: str = "",
        email: str = "",
        id: int | None = None,
    ):

        self.name = name
        self.phone_number = phone_number
        self.email = email

        if aliases is None:

            self.aliases = self.generate_aliases()

        else:

            self.aliases = aliases

        self.id = id

    def generate_aliases(self) -> set[str]:

        aliases = set()
        for name in self.name:
            aliases.add(name.lower())

        return aliases
