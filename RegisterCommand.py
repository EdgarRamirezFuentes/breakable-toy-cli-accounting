from  Command import Command
from collections import defaultdict
import re

class RegisterCommand(Command):
    def __init__(self, file):
        super().__init__(file)
        self.__accounts = defaultdict(list)