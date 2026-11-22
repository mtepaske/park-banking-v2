import sqlite3
from decimal import Decimal

from models.account import Account
from models.balance import Balance
from models.charge import Charge
from models.person import Person
from models.site import Site
from services.date import get_date_from_str
from services.settings import APP_DIRECTORY, get_setting

db_folder = APP_DIRECTORY / get_setting("db_path")
db_folder.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    """
    Establish the database connection

    Returns:
        The database connection
    """

    db_path = db_folder / "database.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    return connection


def disconnect(connection: sqlite3.Connection) -> None:
    """
    Close a database connection

    Args:
        connection: The connection to close
    """

    connection.close()


def initialise_database(connection: sqlite3.Connection) -> None:
    """
    Initialise an empty database with empty tables

    Args:
        connection: The database connection
    """

    with connection:

        # Accounts table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site_id INTEGER NOT NULL,
            balance_id INTEGER NOT NULL,
            primary_id INTEGER NOT NULL,
            secondary_id INTEGER,
            active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # Ensure sites don't have two active accounts
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                unique_active_site_id
            ON accounts (site_id)
            WHERE active = 1
        """)

        # Sites table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY,
            site_number INTEGER NOT NULL,
            cabin INTEGER NOT NULL,
            ac INTEGER NOT NULL, 
            sewer INTEGER NOT NULL
            )
        """)

        # Balance table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS balances (
            id INTEGER PRIMARY KEY,
            balance REAL NOT NULL
            )
        """)

        # Persons table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            aliases TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            )
        """)

        # Charges table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS charges (
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            detials TEXT NOT NULL,
            particulars TEXT NOT NULL
            )
        """)

        # Ignore table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ignore (
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL
            )
        """)


class Repository:

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        return self.connection.execute(query, parameters)

    def executemany(self, query: str, parameters: list[tuple]) -> sqlite3.Cursor:
        return self.connection.executemany(query, parameters)

    def load_accounts(self):
        account_rows = self.execute("""
            SELECT *
            FROM accounts
            """).fetchall()

        accounts = []

        for account in account_rows:

            id = account["id"]
            site = self.load_site(account["site_id"])
            balance = self.load_balance(
                account["balance_id"], annual_fee=site.calc_annual_fees()
            )
            primary = self.load_person(account["primary_id"])
            secondary = self.load_person(account["secondary_id"])
            active = account["active"]
            history = self.load_history(id)

            accounts.append(
                Account(
                    id=id,
                    site=site,
                    balance=balance,
                    primary=primary,
                    secondary=secondary,
                    active=active,
                )
            )
            account.hiostory = history

        return accounts

    def load_balance(self, id: int, annual_fee: Decimal) -> Balance:
        _, balance = self.execute(
            """
            SELECT *
            FROM balances
            WHERE id = ?
            """,
            (id,),
        ).fetchone()
        return Balance(id=id, balance=balance, annual_fees=annual_fee)

    def load_site(self, id: int) -> Site:
        _, site_number, cabin, ac, sewer = self.execute(
            """
            SELECT *
            FROM sites
            WHERE id = ?
            """,
            (id,),
        ).fetchone()
        return Site(
            id=id,
            site_number=site_number,
            cabin=bool(cabin),
            ac=bool(ac),
            sewer=bool(sewer),
        )

    def load_person(self, id: int) -> Person:
        _, name, aliases, phone, email = self.execute(
            """
            SELECT *
            FROM persons
            WHERE id = ?
            """,
            (id,),
        ).fetchone()
        return Person(
            id=id,
            name=name,
            aliases=aliases.split(","),
            phone_number=phone,
            email=email,
        )

    def load_history(self, account_id: int) -> set[Charge]:
        history_rows = self.execute(
            """
            SELECT *
            FROM history
            WHERE account_id = ?
        """,
            (account_id,),
        )
        return {
            Charge(
                date=get_date_from_str(row["date"]),
                amount=Decimal(row["amount"]),
                details=row["details"],
                particulars=row["particulars"],
            )
            for row in history_rows
        }

    def load_ignore(self):
        pass

    def save_accounts(self, accounts: list[Account]):

        with self.connection:

            insert = 0
            update = 0

            for account in accounts:
                inserted = self._save_account(account)

                if inserted:
                    insert += 1
                else:
                    update += 1

        return {"Inserted": insert, "Updated": update}

    def _save_account(self, account: Account):

        site_id = self._save_site(account.site)
        balance_id = self._save_balance(account.balance)
        primary_id = self._save_person(account.primary)
        secondary_id = self._save_person(account.secondary)

        if account.id is None:
            cursor = self.execute(
                """
                INSERT INTO accounts (
                site_id = ?,
                balance_id = ?,
                primary_id = ?,
                secondary_id = ?,
                active = ?
                ) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    site_id,
                    balance_id,
                    primary_id,
                    secondary_id,
                    int(account.active),
                ),
            )

            account.id = cursor.lastrowid

            return True

        else:
            cursor = self.execute(
                """
                UPDATE accounts
                SET site_id = ?,
                balance_id = ?,
                primary_id = ?,
                secondary_id = ?,
                active = ?
                WHERE id = ?
            """,
                (site_id, balance_id, primary_id, secondary_id, int(account.active)),
            )

            return False

    def _save_site(self, site: Site) -> int:

        if site.id is None:
            cursor = self.execute(
                """
                INSERT INTO sites (
                site_number = ?,
                cabin = ?,
                ac = ?,
                sewer = ?,
                )
            """,
                (site.site_number, int(site.cabin), int(site.ac), int(site.sewer)),
            )

            site.id = cursor.lastrowid
            assert site.id is not None
            return site.id

        else:
            cursor = self.execute(
                """
                UPDATE sites
                SET site_number = ?,
                cabin = ?,
                ac = ?,
                sewer = ?,
                WHERE id = ?
            """,
                (
                    site.site_number,
                    int(site.cabin),
                    int(site.ac),
                    int(site.sewer),
                    int(site.id),
                ),
            )

            return site.id

    def _save_balance(self, balance: Balance) -> int:

        if balance.id is None:
            cursor = self.execute(
                """
                INSERT INTO balances (
                balance = ?
                )
            """,
                (balance.balance,),
            )
            balance.id = cursor.lastrowid

            assert balance.id is not None
            return balance.id

        else:
            cursor = self.execute(
                """
                UPDATE balances
                SET balance = ?
                WHERE id = ?
            """,
                (balance.balance, balance.id),
            )

            return balance.id

    def _save_person(self, person: Person | None) -> int:

        if person is None:
            return 0

        if person.id is None:
            cursor = self.execute(
                """
                INSERT INTO persons (
                name = ?,
                aliases = ?,
                phone = ?,
                email = ?
                )
            """,
                (person.name, person.aliases, person.phone_number, person.email),
            )
            person.id = cursor.lastrowid

            assert person.id is not None
            return person.id

        else:

            cursor = self.execute(
                """
                UPDATE persons
                SET name = ?,
                aliases = ?,
                phone = ?,
                email = ?
                WHERE id = ?
            """,
                (
                    person.name,
                    ",".join(person.aliases),
                    person.phone_number,
                    person.email,
                    person.id,
                ),
            )
            return person.id

    def save_ignore(self, words_to_ignore: set[str]) -> None:
        pass
