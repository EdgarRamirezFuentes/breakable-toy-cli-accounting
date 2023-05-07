import re
from Command import Command
from collections import defaultdict

class BalanceCommand(Command):
    def __init__(self, accounts, file):
        super().__init__(file)
        self.__accounts = accounts
        self.__accounts_balance = defaultdict(dict)
        self.__total_balance = defaultdict(float)

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
            self.__get_balance()
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
                # Get the account and the amount
                account, amount = transaction.strip().split('\t', 1)
                concurrency = '$' if '$' in amount else amount.strip().split(' ')[1]
                amount = float(amount.replace(concurrency, '').strip())
                accounts = account.split(':')

                if not self.__accounts_balance.get(accounts[0]):
                    self.__accounts_balance[accounts[0]] = {
                        'balance' : defaultdict(float, {concurrency : amount}),
                        'accounts' : [transaction.strip()]
                    }
                else:
                    self.__accounts_balance[accounts[0]]['balance'][concurrency] += amount
                    self.__accounts_balance[accounts[0]]['accounts'].append(transaction.strip())
                
                self.__total_balance[concurrency] += amount

    def _print_transactions(self):
        """Print the transactions.
        """
        for account, balance in self.__accounts_balance.items():
            print(account, end=':\t| ')
            for currency, amount in balance['balance'].items():
                if currency == '$':
                    print(f'{currency}{amount:.2f}', end=' | ')
                else:
                    print(f'{amount:.2f} {currency}', end=' | ')
            print('\n')
            for transaction in balance['accounts']:
                print(f'\t\t{transaction}')
            print()
        
        print('----------------------------------------------------------------')
        print('Total balance:', end='\n\n')
        for currency, amount in self.__total_balance.items():
            if currency == '$':
                print(f'{currency}{amount:.2f}')
            else:
                print(f'{amount:.2f} {currency}')