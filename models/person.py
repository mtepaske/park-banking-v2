class Person:
    """
    Represents a person and tracks their contact information

    Attributes
    ----------
    name : The persons name
    phone_number : The persons phone number
    email : The persons email address
    aliases : The aliases used in matching
    id : The database id for the person

    """

    def __init__(
        self,
        name: str,
        aliases: set[str] | None = None,
        phone_number: str = "",
        email: str = "",
        id: int | None = None,
    ) -> None:
        """
        Initialises the class

        Parameters
        ----------
        name : str
            The name of the person

        aliases : set[str] | None
            The aliases for the person. Used in matching

        phone_number : str
            The phone number for the person

        email : str
            The email address of the person

        id : int | None
            The database id
        """

        self.name = name
        self.phone_number = phone_number
        self.email = email

        if aliases is None:

            self.aliases = self.generate_aliases()

        else:

            self.aliases = aliases

        self.id = id

    def generate_aliases(self) -> set[str]:
        """
        Generate default aliases from the name

        Returns
        -------
        set[str]
        """

        aliases = set()
        for name in self.name:
            aliases.add(name.lower())

        return aliases
