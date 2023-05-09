import re
from Command import Command

class PrintCommand(Command):
    def __init__(self, accounts, sort, file):
        super().__init__(file)
        self.__accounts = accounts
        self.__sort = sort

    def execute(self):
        with open(f'ledger_files/{self.get_file()}', 'r') as f:
            transactions = ''.join(f.readlines())

            # Checking if the file contains an include statement
            included_files = self._find_included_files(transactions)
            if included_files:
                transactions = self._get_included_transactions(included_files)

            transactions = self._clean_transactions(transactions)
            self._operations_to_dict(transactions)
            self._fill_empty_currencies()

            # If only sort is provided, print the transactions sorted by date
            if self.__accounts:
                self._filter_accounts(self.__accounts)

            if self.__sort:
                self._sort_transactions_by_date()
                
            # If no arguments are provided, print all the transactions
            self._print_transactions()
