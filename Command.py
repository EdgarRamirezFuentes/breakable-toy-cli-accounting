from collections import defaultdict, OrderedDict
import re
import datetime

class Command():
    """The base class for all the commands."""

    def __init__(self, file:str) -> None:
        self._file = file
        self._operations = defaultdict(list)

    def set_file(self, file:str) -> None:
        """Set the file.

        Args:
            file {str} -- The file.
        """
        self._file = file

    def set_operations(self, operations:dict) -> None:
        """Set the operations.

        Args:
            operations {dict} -- The operations.
        """
        self._operations = operations

    def get_file(self) -> str:
        """Get the file.

        Returns:
            str -- The file.
        """
        return self._file
    
    def get_operations(self) -> dict:
        """Get the operations.

        Returns:
            dict -- The operations.
        """
        return self._operations

    def _find_included_files(self, lines:str) -> list:
        """Find the files to include.
        
        Args:
            lines {str} -- The lines to search.
            
        Returns:
            list -- The list of files to include.
        """
        include_regex = re.compile(r'!include\s(.*)')
        include_match = include_regex.findall(lines)
        return [file for file in include_match]
    
    def _get_included_transactions(self, files:list) -> str:
        """Get the transactions from the included files.
        
        Args:
            files {list} -- The list of files to include.
            
        Returns:
            list -- The list of transactions from the included files.
        """
        try:
            transactions = ''

            # For each included file, get the transactions
            for file in files:
                with open(f'ledger_files/{file}', 'r') as f:
                    transactions += ''.join(f.readlines())
            return transactions
        except FileNotFoundError:
            print('An included file was not found.')
            raise SystemExit
        
    def _clean_transactions(self, transactions:str) -> str:
        """Remove comments from the transactions.
        
        Args:
            transactions {str} -- The transactions to clean.
            
        Returns:
            str -- The cleaned transactions.
        """
        comment_regex = re.compile(r';.*')
        return comment_regex.sub('', transactions)
        
    def _operations_to_dict(self, transactions:str) -> dict:
        """Convert the transactions to a dictionary.
        
        Args:
            transactions {str} -- The transactions to convert.
            
        Returns:
            dict -- The transactions as a dictionary.
        """
        date_regex = re.compile(r'^\d{4}\/\d{1,2}\/\d{1,2}.+$')
        current_operation = ''

        for line in transactions.splitlines():
            if not line:
                continue
            
            # Check if the line is a operation
            if re.match(date_regex, line):
                # Converts the date to the format YYYY/MM/DD
                date, description = line.split(' ', 1)
                date = datetime.datetime.strptime(date, '%Y/%m/%d').date().__str__()

                # Get the key for the operations dictionary
                current_operation = date + ' ' + description
            else:
                # Add the transaction to the operation it belongs
                self._operations[current_operation].append(line)

    def _print_transactions(self) -> None:
        """Print the transactions.
        """
        for operation, transactions in self._operations.items():
            if transactions:
                print(operation)
                for transaction in transactions:
                    account, value = transaction.strip().split('\t', 1)

                    # Truncate the account name if it is too long
                    account = account.strip()[:12] + '...' \
                        if len(account.strip()) > 12 else \
                        account.strip() + ' ' * (15 - len(account.strip()))
                    
                    account = '\033[34m' + account + '\033[31m' if value.strip().startswith('-') else '\033[34m' + account + '\033[32m'
                    print(f'\t{account:>12}{value.strip():>50}')
                    print('\033[0m', end='')
                    
    def _fill_empty_currencies(self) -> None:
        """Fill the empty currencies in the transactions.
        """
        for transactions in self._operations.values():
            previous_concurrency = ''
            for i, transaction in enumerate(transactions):
                transaction_components = transaction.lstrip().split('\t', 1)

                if len(transaction_components) == 1:
                    cash_regex = re.compile(r'^-?\$.*$')
                    # Cash
                    if re.match(cash_regex, previous_concurrency.strip()):
                        previous_value = previous_concurrency.strip()
                        current_value = previous_value[1:] if previous_value.startswith('-') else '-' + previous_value
                    # Crypto
                    else:
                        value, concurrency = previous_concurrency.split(' ', 1)
                        value = value.strip()
                        current_value = value[1:] + ' ' + concurrency if value.startswith('-') else '-' + value + ' ' + concurrency
                        
                    previous_concurrency = current_value
                    transaction_components.append(current_value)
                    transactions[i] = '\t' + '\t'.join(transaction_components)
                else:
                    previous_concurrency = transaction_components[1]

    def _sort_transactions_by_date(self) -> None:
        """Sort the transactions by date in asc.
        
        Returns:
            OrderedDict -- The ordered transactions.
        """
        # Sort the transactions by date (The key of the dictionary)
        self._operations = OrderedDict(sorted(self._operations.items()))

    def _filter_accounts(self, accounts:list) -> None:
        """Filter the transactions by account.
        
        Args:
            accounts {list} -- The list of accounts to filter.
        """
        for operation, transactions in self._operations.items():
            new_transactions = []

            for transaction in transactions:
                # Check if the transaction contains any of the accounts
                for account in accounts:
                    # The account can be in the beginning, middle or end of the transaction
                    account_regex = re.compile(r':?{}:?'.format(account))
                    if re.search(account_regex, transaction):
                        new_transactions.append(transaction)
                        break

            # Replace the transactions with the filtered ones
            self._operations[operation] = new_transactions

    def _set_price_color(self, amount:float, currency:str) -> str:
        """Set the color of the price.
        
        Args:
            amount {float} -- The amount.
            currency {str} -- The currency.
            
        Returns:
            str -- The colored price.
        """
        if currency == '$':
            if amount < 0:
                return f'\033[31m{currency}{amount:.2f}\033[0m'
            else:
                return f'\033[32m{currency}{amount:.2f}\033[0m'
        else:
            if amount < 0:
                return f'\033[31m{amount:.2f} {currency}\033[0m'
            else:
                return f'\033[32m{amount:.2f} {currency}\033[0m'
