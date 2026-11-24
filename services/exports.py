import csv

from models.account import Account
from models.charge import Charge
from models.site import Site
from services.settings import APP_DIRECTORY, get_setting

# Sets the folder to export to based on current settings
export_folder = APP_DIRECTORY / get_setting("exports_folder")
export_folder.mkdir(parents=True, exist_ok=True)


def export_accounts_to_csv(accounts: list[Account], filename: str) -> None:
    fieldnames = [
        "ID",
        "Site Number",
        "Primary Site Holder",
        "Secondary Site Holder",
        "Annual Fees",
        "Remianing From This Fincial Year",
        "Outstanding From Previous Fincial Years",
        "Credit",
        "Total Balance",
        "Active",
        "Primary ID",
        "Primary Aliases",
        "Primary Phone Number",
        "Primary Email",
        "Secondary ID",
        "Secondary Aliases",
        "Secondary Phone Number",
        "Secondary Email",
        "Cabin",
        "AC",
        "Sewer",
    ]

    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for account in accounts:
            writer.writerow(account.to_dict())


def export_sites(sites: set[Site], filename: str) -> None:
    fieldnames = ["Site Number", "Cabin", "AC", "Sewer"]

    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for site in sites:
            writer.writerow(site.to_dict())


def export_history(history: set[Charge], filename: str) -> None:
    fieldnames = ["Date", "Description", "Debit", "Credit"]

    with open(
        f"{export_folder / filename}.csv", "w", newline="", encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for charge in history:
            writer.writerow(charge.to_history_dict())
