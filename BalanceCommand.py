import re
from Command import Command
from collections import defaultdict

class BalanceCommand(Command):
    def __init__(self, accounts, file, full_balance=False):
        super().__init__(file)
        self.__accounts = accounts
        self.__accounts_balance = defaultdict(dict)
        self.__total_balance = defaultdict(float)
        self.__full_balance = full_balance

    def execute(self) -> None:
        with open(f'ledger_files/{self.get_file()}', 'r') as f:
            transactions = ''.join(f.readlines())

            # Checking if the file contains an include statement
            included_files = self._find_included_files(transactions)
            if included_files:
                transactions = self._get_included_transactions(included_files)

            transactions = self._clean_transactions(transactions)
            self._operations_to_dict(transactions)
            self._fill_empty_currencies()

            # If accounts are provided, print only the transactions for those accounts
            if self.__accounts:
                self.__filter_accounts()

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

    def __get_balance(self) -> None:
        """Get the balance of the accounts.
        """

        for transactions in self._operations.values():
            for transaction in transactions:
                # Get the account and the amount
                account, amount = transaction.strip().split('\t', 1)
                currency = '$' if '$' in amount else amount.strip().split(' ')[1]
                amount = float(amount.replace(currency, '').strip())
                accounts = account.split(':')

                if not self.__accounts_balance.get(accounts[0].strip()):
                    self.__accounts_balance[accounts[0].strip()] = {
                        'balance': defaultdict(float),
                        'accounts': defaultdict(defaultdict)
                    }

                current_account = self.__accounts_balance[accounts[0].strip()]
                current_account['balance'][currency] += amount
                
                if self.__full_balance:
                    if len(accounts) > 1:
                        for subaccount in accounts[1:]:
                            if not current_account['accounts'].get(subaccount.strip()):
                                current_account['accounts'][subaccount.strip()] = {
                                    'balance': defaultdict(float),
                                    'accounts': defaultdict(defaultdict)
                                }

                            current_account['accounts'][subaccount.strip()]['balance'][currency] += amount
                            current_account = current_account['accounts'][subaccount.strip()]

                self.__total_balance[currency] += amount

    def _print_transactions(self) -> None:
        """Print the balance of the root accounts, and its subaccounts.
        """
        for account, data in self.__accounts_balance.items():
            account = account.strip()[:12] + '...' \
                        if len(account.strip()) > 12 else \
                        account.strip() + '-' * (15 - len(account.strip()))
            
            account = '\033[34m' + account + '\033[0m'

            print(account, end=' ')

            balance = data['balance']

            for currency, amount in balance.items():
                print(self._set_price_color(amount, currency), end=' ')
            subaccounts = data['accounts']

            # If the user wants to see the full balance, print the subaccounts
            if self.__full_balance:
                for subaccount, data in subaccounts.items():
                    self._print_subaccounts(subaccount, data, 1) 
                print()       

            print()

        # Print the total balance
        print('-' * 60)
        for currency, amount in self.__total_balance.items():
            print(self._set_price_color(amount, currency))

    def _print_subaccounts(self, account:str, data:dict, level:int=1) -> None:
        """Print the subaccounts of an account.
        """
        tabs = '\t' * level

        # Truncate the account name if it is too long
        account = account.strip()[:12] + '...' \
                    if len(account.strip()) > 12 else \
                    account.strip() + '-' * (15 - len(account.strip()))
        
        account = '\033[33m' + account + '\033[0m'

        print(f'\n{tabs}{account}', end=' ')

        balance = data['balance']
        for currency, amount in balance.items():
            print(self._set_price_color(amount, currency), end=' ')

        subaccounts = data['accounts']

        for subaccount, data in subaccounts.items():
            self._print_subaccounts(subaccount, data, level + 1)









            