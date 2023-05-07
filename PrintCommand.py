import re
from collections import OrderedDict
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
            if not self.__accounts and self.__sort:
                self.__sort_transactions_by_date()
   
            # If accounts are provided, print only the transactions for those accounts
            elif self.__accounts and not self.__sort:
                self.__filter_accounts()

            # If sort and accounts is provided, print the transactions sorted by date
            elif self.__accounts and self.__sort:
                self.__filter_accounts()
                self.__sort_transactions_by_date()
                
            # If no arguments are provided, print all the transactions
            self._print_transactions()
                    
    def __sort_transactions_by_date(self):
        """Sort the transactions by date in asc.
        
        Returns:
            OrderedDict -- The ordered transactions.
        """
        # Sort the transactions by date (The key of the dictionary)
        self._operations = OrderedDict(sorted(self._operations.items()))

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
