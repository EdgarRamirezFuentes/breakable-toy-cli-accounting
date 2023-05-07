"""A breakable toy CLI for managing a ledger of transactions.
"""
import argparse
from PrintCommand import PrintCommand
from BalanceCommand import BalanceCommand
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Add the print command
    print = subparsers.add_parser("print", help="Print the ledger.")
    print.add_argument('-f', '--file', help='The ledger file to use.', default="index.ledger")
    print.add_argument('-a', '--account', help='The accounts to print.', nargs='+')
    print.add_argument('-s', '--sort', help='The accounts to print.')

    # Add the balance command
    balance = subparsers.add_parser("balance", help="Print the balance.")
    balance.add_argument('-f', '--file', help='The ledger file to use.', default="index.ledger")
    balance.add_argument('-a', '--account', help='The accounts to print.', nargs='+')


    args = parser.parse_args()
    
    if args.command == "print":
        command = PrintCommand(args.account, args.sort, args.file)
        command.execute()
    elif args.command == "balance":
        command = BalanceCommand(args.account, args.file)
        command.execute()



