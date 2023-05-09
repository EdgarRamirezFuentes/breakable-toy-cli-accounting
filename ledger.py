"""A breakable toy CLI for managing a ledger of transactions.
"""
import argparse
from PrintCommand import PrintCommand
from BalanceCommand import BalanceCommand
from RegisterCommand import RegisterCommand


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Add the print command
    print = subparsers.add_parser("print", help="Print the ledger.", aliases=['p'])
    print.add_argument('-f', '--file', help='The ledger file to use.', default="index.ledger")
    print.add_argument('-a', '--account', help='The accounts to print.', nargs='+')
    print.add_argument('-s', '--sort', help='The accounts to print.')
    print.add_argument('--price-db', help='The prices db file', default="prices_db")

    # Add the balance command
    balance = subparsers.add_parser("balance", help="Print the balance.", aliases=['bal', 'b'])
    balance.add_argument('-f', '--file', help='The ledger file to use.', default="index.ledger")
    balance.add_argument('-a', '--account', help='The accounts to print.', nargs='+')
    balance.add_argument('--full', help='The accounts to print.', action='store_true')
    balance.add_argument('--price-db', help='The prices db file', default="prices_db")

    # Add the register commannd
    register = subparsers.add_parser("register", help="Print the register.", aliases=['reg', 'r'])
    register.add_argument('-f', '--file', help='The ledger file to use.', default="index.ledger")
    register.add_argument('-a', '--account', help='The accounts to print.', nargs='+')
    register.add_argument('-s', '--sort', help='The accounts to print.')
    register.add_argument('--price-db', help='The prices db file', default="prices_db")


    args = parser.parse_args()
    
    if args.command == "print" or args.command == "p":
        command = PrintCommand(args.account, args.sort, args.file)
        command.execute()
    elif args.command == "balance" or args.command == "bal" or args.command == "b":
        command = BalanceCommand(args.account, args.file, args.full)
        command.execute()
    elif args.command == "register" or args.command == "reg" or args.command == "r":
        command = RegisterCommand(args.account, args.sort, args.file)
        command.execute()
    else:
        print("Command not found.")



