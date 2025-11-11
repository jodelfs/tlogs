import sys

class TLLogger:
    LEVELS = { 'DEBUG': 1, 'INFO': 2, 'WARNING': 3, 'ERROR': 4, 'CRITICAL': 5 }

    def __init__(self, level='INFO'):
        self.level = self.LEVELS.get(level.upper(), 2)

    def log(self, level, message):
        if self.LEVELS[level] >= self.level:
            print(f"{level}: {message}", file=sys.stdout)

    def debug(self, message):
        self.log('DEBUG', message)

    def info(self, message):
        self.log('INFO', message)

    def warning(self, message):
        self.log('WARNING', message)

    def error(self, message):
        self.log('ERROR', message)

    def critical(self, message):
        self.log('CRITICAL', message)

logger = TLLogger(level='DEBUG')