import re
from collections import defaultdict, OrderedDict
import datetime

class PrintCommand():
    def __init__(self, accounts, sort, file):
        self.__accounts = accounts
        self.__sort = sort
        self.__file = file
        # The operations dictionary will contain the transactions grouped by operation
        self.__operations = defaultdict(list)

    def execute(self):
        with open(f'ledger_files/{self.__file}', 'r') as f:
            transactions = ''.join(f.readlines())

            # Checking if the file contains an include statement
            included_files = self.__find_included_files(transactions)
            if included_files:
                transactions = self.__get_included_transactions(included_files)

            transactions = self.__clean_transactions(transactions)
            self.__operations_to_dict(transactions)


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
            self.__print_transactions()

    def __clean_transactions(self, transactions):
        """Remove comments from the transactions.
        
        Args:
            transactions {str} -- The transactions to clean.
            
        Returns:
            str -- The cleaned transactions.
        """
        comment_regex = re.compile(r';.*')
        return comment_regex.sub('', transactions)
                    
    def __find_included_files(self, lines):
        """Find the files to include.
        
        Args:
            lines {str} -- The lines to search.
            
        Returns:
            list -- The list of files to include.
        """
        include_regex = re.compile(r'!include\s(.*)')
        include_match = include_regex.findall(lines)
        return [file for file in include_match]

    def __get_included_transactions(self, files):
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
        
    def __operations_to_dict(self, transactions):
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
                self.__operations[current_operation].append(line)
        
    def __filter_accounts(self):
        """Filter the transactions by account."""
        for operation, transactions in self.__operations.items():
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
            self.__operations[operation] = new_transactions
                    
    def __sort_transactions_by_date(self):
        """Sort the transactions by date in asc.
        
        Returns:
            OrderedDict -- The ordered transactions.
        """
        # Sort the transactions by date (The key of the dictionary)
        self.__operations = OrderedDict(sorted(self.__operations.items()))
    
    def __print_transactions(self):
        """Print the transactions.
        """
        for operation, transactions in self.__operations.items():
            if transactions:
                print(operation)
                for transaction in transactions:
                    print(transaction)
    



    