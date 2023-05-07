from collections import defaultdict
import re
import datetime

class Command():
    """The base class for all the commands."""

    def __init__(self, file) -> None:
        self._file = file
        self._operations = defaultdict(list)

    def set_file(self, file) -> None:
        """Set the file.

        Args:
            file {str} -- The file.
        """
        self._file = file

    def set_operations(self, operations) -> None:
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

    def _find_included_files(self, lines) -> list:
        """Find the files to include.
        
        Args:
            lines {str} -- The lines to search.
            
        Returns:
            list -- The list of files to include.
        """
        include_regex = re.compile(r'!include\s(.*)')
        include_match = include_regex.findall(lines)
        return [file for file in include_match]
    
    def _get_included_transactions(self, files) -> str:
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
        
    def _clean_transactions(self, transactions):
        """Remove comments from the transactions.
        
        Args:
            transactions {str} -- The transactions to clean.
            
        Returns:
            str -- The cleaned transactions.
        """
        comment_regex = re.compile(r';.*')
        return comment_regex.sub('', transactions)
        
    def _operations_to_dict(self, transactions) -> dict:
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

    def _print_transactions(self):
        """Print the transactions.
        """
        for operation, transactions in self._operations.items():
            if transactions:
                print(operation)
                for transaction in transactions:
                    print(transaction)

    def _fill_empty_currencies(self):
        """Fill the empty currencies in the transactions.
        """

        for operation, transactions in self._operations.items():
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


    
