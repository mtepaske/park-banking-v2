import sqlite3
from decimal import Decimal

from models.account import Account
from models.charge import Charge
from models.person import Person
from models.site import Site
from services.date import get_date_from_str, get_str_from_date
from services.settings import APP_DIRECTORY, get_setting

db_folder = APP_DIRECTORY / get_setting("db_path")
db_folder.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    db_path = db_folder / "database.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    return connection


def disconnect(connection: sqlite3.Connection) -> None:
    connection.close()


def initialise_database(connection: sqlite3.Connection) -> None:
    with connection:

        # Accounts table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            site_id INTEGER NOT NULL,
            primary_id INTEGER NOT NULL,
            secondary_id INTEGER,
            active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (primary_id) REFERENCES people(id),
            FOREIGN KEY (secondary_id) REFERENCES people(id),
            FOREIGN KEY (site_id) REFERENCES sites(site_number)
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
            site_number INTEGER PRIMARY KEY,
            cabin INTEGER NOT NULL,
            ac INTEGER NOT NULL, 
            sewer INTEGER NOT NULL
            )
        """)

        # Persons table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            aliases TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
            )
        """)

        # Charges table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS charges (
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            details TEXT NOT NULL,
            particulars TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)

        # Ignore table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ignore (
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL UNIQUE
            )
        """)


class Repository:

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        return self.connection.execute(query, parameters)

    def executemany(self, query: str, parameters: list[tuple]) -> sqlite3.Cursor:
        return self.connection.executemany(query, parameters)

    def load_accounts(self) -> set[Account]:
        account_rows = self.execute("""
            SELECT *
            FROM accounts
            """).fetchall()

        accounts = set()

        for account in account_rows:

            id = account["id"]
            site = self.load_site(account["site_id"])
            primary = self.load_person(account["primary_id"])
            secondary = self.load_person(account["secondary_id"])
            history = self.load_history(id)
            active = account["active"]

            assert primary is not None

            accounts.add(
                Account(
                    id=id,
                    site=site,
                    primary=primary,
                    secondary=secondary,
                    history=history,
                    active=bool(active),
                )
            )

        return accounts

    def load_site(self, id: int) -> Site:
        _, cabin, ac, sewer = self.execute(
            """
            SELECT *
            FROM sites
            WHERE site_number = ?
            """,
            (id,),
        ).fetchone()
        return Site(
            site_number=id,
            cabin=bool(cabin),
            ac=bool(ac),
            sewer=bool(sewer),
        )

    def load_person(self, id: int | None) -> Person | None:

        if id is None:
            return None

        _, name, aliases, phone, email = self.execute(
            """
            SELECT *
            FROM people
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
            FROM charges
            WHERE account_id = ?
        """,
            (account_id,),
        ).fetchall()
        return {
            Charge(
                date=get_date_from_str(row["date"]),
                amount=Decimal(row["amount"]),
                details=row["details"],
                particulars=row["particulars"],
                id=row["id"],
            )
            for row in history_rows
        }

    def load_ignore(self) -> set[str]:
        ignore_rows = self.execute("""
            SELECT word
            FROM ignore
            """)
        return {word for word in ignore_rows}

    def save_accounts(self, accounts: set[Account]) -> dict[str, int]:

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

    def _save_account(self, account: Account) -> bool:

        site_id = self._save_site(account.site)
        primary_id = self._save_person(account.primary)
        secondary_id = self._save_person(account.secondary)

        if account.id is None:
            cursor = self.execute(
                """
                INSERT INTO accounts (
                site_id,
                primary_id,
                secondary_id,
                active
                ) 
                VALUES (?, ?, ?, ?)
                """,
                (
                    site_id,
                    primary_id,
                    secondary_id,
                    int(account.active),
                ),
            )

            account.id = cursor.lastrowid
            self._save_history(account)

            return True

        else:
            cursor = self.execute(
                """
                UPDATE accounts
                SET site_id = ?,
                primary_id = ?,
                secondary_id = ?,
                active = ?
                WHERE id = ?
            """,
                (site_id, primary_id, secondary_id, int(account.active), account.id),
            )
            self._save_history(account)

            return False

    def _save_site(self, site: Site) -> int:
        self.execute(
            """
            INSERT INTO sites (
            site_number,
            cabin,
            ac,
            sewer
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(site_number)
            DO UPDATE SET
            cabin = excluded.cabin,
            ac = excluded.ac,
            sewer = excluded.sewer
        """,
            (site.site_number, site.cabin, site.ac, site.sewer),
        )

        return site.site_number

    def _save_person(self, person: Person | None) -> int | None:

        if person is None:
            return None

        if person.id is None:
            cursor = self.execute(
                """
                INSERT INTO people (
                name,
                aliases,
                phone,
                email
                )
                VALUES (?, ?, ?, ?)
            """,
                (
                    person.name,
                    ",".join(person.aliases),
                    person.phone_number,
                    person.email,
                ),
            )
            person.id = cursor.lastrowid

            assert person.id is not None
            return person.id

        else:

            self.execute(
                """
                UPDATE people
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

    def _save_history(self, account: Account) -> None:
        assert account.id is not None
        for charge in account.history:
            if charge.id is None:
                cursor = self.execute(
                    """
                    INSERT INTO charges (
                    account_id,
                    date,
                    amount,
                    details,
                    particulars
                    )
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        account.id,
                        get_str_from_date(charge.date),
                        str(charge.amount),
                        charge.details,
                        charge.particulars,
                    ),
                )
                charge.id = cursor.lastrowid

            else:

                self.execute(
                    """
                    UPDATE charges
                    SET account_id = ?,
                    date = ?,
                    amount = ?,
                    details = ?,
                    particulars = ?
                    WHERE id = ?
                """,
                    (
                        account.id,
                        get_str_from_date(charge.date),
                        str(charge.amount),
                        charge.details,
                        charge.particulars,
                        charge.id,
                    ),
                )

    def save_ignore(self, words_to_ignore: set[str]) -> None:
        with self.connection:
            self.execute("""DELETE FROM ignore""")
            self.executemany(
                """INSERT INTO ignore (word) VALUES (?)""",
                [(word,) for word in words_to_ignore],
            )
