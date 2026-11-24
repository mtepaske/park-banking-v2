import csv
from decimal import Decimal

from models.account import Account
from models.charge import Charge
from models.site import Site
from services.settings import APP_DIRECTORY, get_setting

import_folder = APP_DIRECTORY / get_setting("imports_folder")


def import_statement(filename: str) -> set[Charge]:
    with open(f"{import_folder / filename}", newline="", encoding="utf-8-sig") as file:

        charges = set()
        reader = csv.DictReader(file)
        for row in reader:

            if Decimal(row["Amount"]) < 0:
                continue
            if row["Transaction Details"] == "CASH":
                continue
            charges.add(Charge.from_csv(row))

        return charges


def import_accounts(filename: str) -> set[Account]:
    with open(f"{import_folder / filename}", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {Account.from_csv(row) for row in reader}


def import_sites(filename: str) -> set[Site]:
    with open(f"{import_folder / filename}", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {Site.from_csv(row) for row in reader}


def import_ignore(filename: str) -> set[str]:
    with open(f"{import_folder / filename}", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {word["Word"] for word in reader}


def import_history(filename: str) -> set[Charge]:
    with open(f"{import_folder / filename}", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {Charge.from_history_csv(row) for row in reader}
