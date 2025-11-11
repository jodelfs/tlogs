from tlexport2db import Export2DB
from tlexport2csv import Export2CSV

class Export:
    def __init__(self, log_data, result):
        self.commands = [Export2DB(log_data, result), Export2CSV(log_data, result)]

    def execute(self):
        for cmd in self.commands:
            cmd.execute()

