"""Analyze 
"""

class Results(object):
    """Set of results for where your cash went every month."""

    

class Analyzer(object):
    """Class that runs through your accounts looking at your cash flow."""

    def __init__(self):
        self.account_map = {}

    def map(self, from_account, to_account):
        """Rewrite ``from_account`` to ``to_account``."""
        self.account_map[from_account] = to_account

    def analyze(self, book):
        pass
