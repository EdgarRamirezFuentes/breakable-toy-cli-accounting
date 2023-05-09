from  Command import Command
from collections import defaultdict
import re

class RegisterCommand(Command):
    def __init__(self, accounts:list, sort:bool, file:str) -> None:
        super().__init__(file)
        self.__accounts = accounts
        self.__sort = sort
        self.__total_balance = defaultdict(float)

    def execute(self) -> None:
        print(f'File: {self.get_file()}')
        with open(f'ledger_files/{self.get_file()}', 'r') as f:
            transactions = ''.join(f.readlines())

            # Checking if the file contains an include statement
            included_files = self._find_included_files(transactions)
            if included_files:
                transactions = self._get_included_transactions(included_files)

            transactions = self._clean_transactions(transactions)
            self._operations_to_dict(transactions)
            self._fill_empty_currencies()

            if self.__accounts:
                self._filter_accounts(self.__accounts)

            if self.__sort:
                self._sort_transactions_by_date()

            self._print_transactions()
    
    def _print_transactions(self) -> None:
        """Print the transactions.
        """
        for operation, transactions in self._operations.items():
            if transactions:
                print(operation)
                for transaction in transactions:      
                    # Get the account and the amount
                    account, amount = transaction.strip().split('\t', 1)
                    currency = '$' if '$' in amount else amount.strip().split(' ')[1]
                    amount = float(amount.replace(currency, '').strip())
                    self.__total_balance[currency] += amount

                    # Truncate the account name if it is too long
                    account = account.strip()[:12] + '...' \
                        if len(account.strip()) > 12 else \
                        account.strip() + ' ' * (15 - len(account.strip()))
                    
                    account = '\033[34m' + account  + '\033[0m'

                    current_balance = ''

                    # Print the running balance
                    for balance_currency, balance_amount in self.__total_balance.items():
                        current_balance += self._set_price_color(balance_amount, balance_currency) + ' '

                    print(f'\t{account:>12}{self._set_price_color(amount, currency):>40}\t\t{current_balance}')
                    
                print()
                    


