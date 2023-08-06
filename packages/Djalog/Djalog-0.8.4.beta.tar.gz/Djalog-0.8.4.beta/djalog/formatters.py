import logging

from djalog import colored

class ColoredFormatter(logging.Formatter):
    """
    Formatter which uses ANSI escape characters
    to color the output. Use it with StreamHandler
    - others may simply returns crappy output.
    """
    
    def format(self, record):
        """
        Changes record's levelname to use with COLORS enum
        """
        
        levelname = record.levelname
        start = colored.COLOR_SEQ % (colored.COLORS[levelname])
        def_record = logging.Formatter.format(self, record)
        end = colored.RESET_SEQ
        
        colored_record = start + def_record + end
        return colored_record

