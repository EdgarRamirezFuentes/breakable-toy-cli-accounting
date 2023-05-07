import re
from Command import Command

class BalanceCommand(Command):
    def __init__(self, accounts, file):
        super().__init__(file)
        self.__accounts = accounts

    def execute(self):
        with open(f'ledger_files/{self.get_file()}', 'r') as f:
            transactions = ''.join(f.readlines())

            # Checking if the file contains an include statement
            included_files = self._find_included_files(transactions)
            if included_files:
                transactions = self._get_included_transactions(included_files)

            transactions = self._clean_transactions(transactions)
            self._operations_to_dict(transactions)

            # If accounts are provided, print only the transactions for those accounts
            if self.__accounts:
                self.__filter_accounts()

            self._fill_empty_currencies()

            # If no arguments are provided, print all the transactions
            #self.__get_balance()
            self._print_transactions()

    def __filter_accounts(self) -> None:
        """Filter the transactions by account."""
        for operation, transactions in self._operations.items():
            new_transactions = []

            for transaction in transactions:
                # Check if the transaction contains any of the accounts
                for account in self.__accounts:
                    # The account can be in the beginning, middle or end of the transaction
                    account_regex = re.compile(r':?{}:?'.format(account))
                    if re.search(account_regex, transaction):
                        new_transactions.append(transaction)
                        break

            # Replace the transactions with the filtered ones
            self._operations[operation] = new_transactions

    def __get_balance(self) -> dict:
        """Get the balance of the accounts.
        """

        for operation, transactions in self._operations.items():
            for transaction in transactions:
                print(transaction.strip().split('\t', 1))

