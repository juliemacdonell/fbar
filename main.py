"""
Main 
~~~~

See README.md for more information on how to use this script.

This script does the following:
    - Queries the YNAB API for user to load information on budgets, accounts, 
    and transactions.
    - Calculates the maximum balance for each account for specified calendar 
    year.
    - Converts the maximum balance into USD.
    - Prints report of maximum balances and date ranges for balance for each 
    account.
"""
import datetime
import functools
import operator
import typing

import prettytable
import yaml
import ynab

TODAY = datetime.date.today()

with open("config.yml") as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)


@functools.lru_cache(maxsize=None)
def get_api(api: str):
    """
    Get an YNAB API instance.

    Parameters:
        api: lowercase name of API resources, e.g. 'accounts'

    Returns:
        API instance
    """
    configuration = ynab.Configuration(
        api_key=dict(Authorization=CONFIG["ynab"]["token"]),
        api_key_prefix=dict(Authorization="Bearer"),
    )
    return operator.methodcaller(
        f"{api.capitalize()}Api", ynab.ApiClient(configuration)
    )(ynab)


def handle_exception(func: typing.Callable) -> typing.Callable:
    """
    Decorator to handle YNAB API exceptions.
    """

    def wrapper(*args):
        """Inner"""
        try:
            return func(*args)
        except ynab.rest.ApiException as e:
            print(f"Exception when calling YNAB API: %f\n")

    return wrapper


@handle_exception
def get_budgets():
    """
    Get budgets.

    Returns:
        List of budgets
    """
    budgets_api = get_api("budgets")
    return budgets_api.get_budgets().data.budgets


@handle_exception
def get_accounts(budget_id: str):
    """
    Get accounts for budget.

    Parameters:
        budget_id: Budget ID

    Returns:
        List of accounts
    """
    accounts_api = get_api("accounts")
    return accounts_api.get_accounts(budget_id).data.accounts


@handle_exception
def get_transactions(budget_id: str, account_id: str):
    """
    Get transactions.

    Parameters:
        budget_id: Budget ID
        account_id: Account ID

    Returns:
        List of transactions
    """
    transactions_api = get_api("transactions")
    return transactions_api.get_transactions_by_account(
        budget_id,
        account_id,
        since_date=f"{CONFIG['year'] - 1}-01-01",  # Ensures all transactions
    ).data.transactions


def main():
    """
    Generates report of maximum balances for all YNAB accounts.
    """
    # Build up accounts.
    accounts = []
    # Iterate through budgets.
    _budgets = get_budgets()
    for _budget in _budgets:
        # Iterate through accounts in budget.
        _accounts = get_accounts(_budget.id)
        for _account in _accounts:
            accounts.append(dict(_account.to_dict(), budget_id=_budget.id))

    # Add transactions to accounts.
    for account in accounts:
        account["transactions"] = sorted(
            [
                transaction.to_dict()
                for transaction in get_transactions(account["budget_id"], account["id"])
                if transaction.cleared in ("cleared", "reconciled")
            ],
            key=operator.itemgetter("date"),
            reverse=True,
        )

    # Calculate max balance for each account.
    for account in accounts:
        current_balance = account["cleared_balance"]
        max_balance = dict(
            balance=current_balance,
            start=account["transactions"][-1]["date"]
            if account["transactions"]
            else datetime.date(2000, 1, 1),
            end=datetime.date.today(),
        )
        for idx, transaction in enumerate(account["transactions"]):
            print(transaction)
            try:
                start = account["transactions"][idx + 1]["date"]
            except IndexError:
                start = account["transactions"][idx]["date"]

            current_balance -= transaction["amount"]

            if transaction["date"].year > CONFIG["year"] or (
                transaction["date"].year == CONFIG["year"]
                and current_balance > max_balance["balance"]
            ):
                max_balance = dict(
                    balance=current_balance,
                    start=start,
                    end=transaction["date"],
                )

        account["max_balance"] = max_balance

    table = prettytable.PrettyTable(
        ["Name", "Max Balance EUR", "Max Balance USD", "Start Date", "End Date"]
    )
    for account in accounts:
        if account["max_balance"]:
            eur_max_balance = round(account["max_balance"]["balance"] / 1000, 2)
            usd_max_balance = round(
                eur_max_balance / CONFIG["currency"]["usd_to_eur"], 2
            )
            start_date = account["max_balance"]["start"]
            end_date = account["max_balance"]["end"]
        else:
            eur_max_balance = 0.00
            usd_max_balance = 0.00
            start_date = datetime.date(CONFIG["year"], 1, 1)
            end_date = datetime.date(CONFIG["year"], 12, 31)

        table.add_row(
            [
                account["name"],
                f"€{eur_max_balance}",
                f"${usd_max_balance}",
                start_date,
                end_date,
            ]
        )

    print(table)


if __name__ == "__main__":
    main()
