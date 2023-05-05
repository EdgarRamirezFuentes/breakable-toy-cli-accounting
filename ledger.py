"""A breakable toy CLI for managing a ledger of transactions.
"""
import argparse
import re
from PrintCommand import PrintCommand
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Add the print command
    register = subparsers.add_parser("print", help="Register an account")
    register.add_argument('-f', '--file', help='The ledger file to use.', required=True)
    register.add_argument('-a', '--account', help='The accounts to print.', nargs='+')
    register.add_argument('-s', '--sort', help='The accounts to print.')


    args = parser.parse_args()
    
    if args.command == "print":
        command = PrintCommand(args.account, args.sort, args.file)
        command.execute()


