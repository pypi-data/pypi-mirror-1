"""The command-line interface to running cashflow."""

import sys
from optparse import OptionParser

from cashflow import open as cashflow_open
from cashflow.format import display
from cashflow.reports import cashflow

def main():
    """Command-line cashflow program (an entry point in `setup.py`)."""

    # Check the command line for validity.

    parser = OptionParser(usage="usage: %prog `filename`")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("you must provide the `filename` of a Gnucash file")

    # Open our input file.

    try:
        book = cashflow_open(args[0])
    except IOError, e:
        sys.stderr.write("cashflow: cannot open file %r: %s\n"
                         % (args[0], e.strerror or e.message))
        sys.exit(1)

    # Run the report and print it out.

    rows = cashflow(book)
    display(rows)
